import http_codes
import asyncio
from sqlalchemy.orm import joinedload
from db_init import db
from flask_restful import Resource, abort, reqparse
from werkzeug.datastructures import FileStorage
from datetime import datetime
from marshmallow import ValidationError
from flask import jsonify, make_response, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Comment, User, Notification, Post
from schemas import CommentGetSchema, CommentCreateSchema, CommentUpdateSchema, UserGetSchema
from text_templates import OBJECT_DOES_NOT_EXIST, OBJECT_DELETED, OBJECT_EDIT_NOT_ALLOWED, OBJECT_DELETE_NOT_ALLOWED
from utilities import is_authorized_error_handler, save_file
from .mixins import PaginationMixin, FilterMixin


parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument("comment_text", location="form")
parser.add_argument("comment_image", type=FileStorage, location="files")


class CommentListView(Resource, PaginationMixin, FilterMixin):
    comments_get_schema = CommentGetSchema(many=True)
    comment_get_schema = CommentGetSchema()
    comment_create_schema = CommentCreateSchema()

    @is_authorized_error_handler()
    @jwt_required()
    def get(self):
        filters = request.args.get("filters")
        sort_by = request.args.get("sort_by")
        sort_order = request.args.get("sort_order", "asc")

        comments_query = Comment.query.options(
            joinedload(Comment.author),
            joinedload(Comment.post),
            joinedload(Comment.parent_comment)
        ).order_by(Comment.comment_id)

        try:
            if filters:
                filter_mappings = {
                    "comment_parent": (Comment.parent_comment, Comment.comment_id),
                    "comment_post": (Comment.post, Post.post_id),
                    "comment_author": (Comment.author, User.user_id)
                }

                comments_query = self.get_filtered_query(
                    query=comments_query,
                    model=Comment,
                    filters=filters,
                    filter_mappings=filter_mappings
                )

            if sort_by:
                column = getattr(User, sort_by)
                sort_mappings = {
                    "comment_author": User.user_id,
                    "comment_parent": Comment.comment_id,
                    "comment_post": Post.post_id,
                }

                if sort_by in sort_mappings:
                    column = sort_mappings.get(sort_by, getattr(Comment, sort_by))

                    if sort_order.lower() == "desc":
                        column = column.desc()

                comments_query = comments_query.order_by(column)

        except AttributeError as e:
            abort(http_codes.HTTP_BAD_REQUEST_400, error_message=str(e))

        response = self.get_paginated_response(
            query=comments_query,
            items_schema=self.comments_get_schema,
            model_plural_name="comments",
            count_field_name="comment_count"
        )

        return response

    @is_authorized_error_handler()
    @jwt_required()
    async def post(self):
        parser_post = parser.copy()
        parser_post.add_argument("comment_post", type=int, location="form")
        parser_post.add_argument("comment_parent", type=int, location="form")
        data = parser_post.parse_args()

        comment_author = User.query.get(get_jwt_identity())
        data["comment_author"] = UserGetSchema(only=("user_id",)).dump(comment_author)
        data["comment_created_at"] = datetime.utcnow().isoformat()
        image_file = data["comment_image"]

        try:
            with db.session.begin():
                comment = self.comment_create_schema.load(data)
                async_tasks = []

                if comment.comment_parent and comment.comment_post != comment.parent_comment.comment_post:
                    abort(http_codes.HTTP_FORBIDDEN_403, error_message="Parent comment has different post.")

                db.session.add(comment)

                if image_file:
                    db.session.add(comment.comment_image)
                    task = save_file(image_file, comment.comment_image.file_url[1:])
                    async_tasks.append(task)

                await asyncio.gather(*async_tasks)

                if comment_author is not comment.post.author:
                    notification_post_commented = Notification(
                        notification_text=f"Your post {comment.post} have been commented.",
                        notification_receiver=comment.post.author,
                        notification_sender_url=f"/comment/{comment.comment_id}"
                    )
                    db.session.add(notification_post_commented)

                if comment.parent_comment and comment.parent_comment.author is not comment_author:
                    notification_comment_answered = Notification(
                        notification_text=f"Your comment {comment.comment_parent} received an answer!",
                        notification_receiver=comment.parent_comment.author,
                        notification_sender_url=f"/comment/{comment.comment_id}"
                    )
                    db.session.add(notification_comment_answered)

            return make_response(jsonify(self.comment_get_schema.dump(comment)), http_codes.HTTP_CREATED_201)
        except ValidationError as e:
            abort(http_codes.HTTP_BAD_REQUEST_400, error_message=str(e))


class CommentDetailedView(Resource):
    comment_get_schema = CommentGetSchema()
    comment_update_schema = CommentUpdateSchema()

    @is_authorized_error_handler()
    @jwt_required()
    def get(self, comment_id):
        comment = Comment.query.get_or_404(comment_id, description=OBJECT_DOES_NOT_EXIST.format("Comment", comment_id))

        return jsonify(self.comment_get_schema.dump(comment))

    @classmethod
    @is_authorized_error_handler()
    @jwt_required()
    async def delete(cls, comment_id):
        comment = Comment.query.get_or_404(comment_id, description=OBJECT_DOES_NOT_EXIST.format("Comment", comment_id))

        editor = User.query.get(get_jwt_identity())
        if editor is not comment.author:
            abort(http_codes.HTTP_FORBIDDEN_403, error_message=OBJECT_DELETE_NOT_ALLOWED.format("comment"))

        comment.delete()

        return {"success": OBJECT_DELETED.format("Comment", comment_id)}, http_codes.HTTP_NO_CONTENT_204

    @is_authorized_error_handler()
    @jwt_required()
    async def put(self, comment_id):
        try:
            with db.session.begin():
                comment = Comment.query.get_or_404(
                    comment_id, description=OBJECT_DOES_NOT_EXIST.format("Comment", comment_id)
                )

                editor = User.query.get(get_jwt_identity())
                if editor is not comment.author:
                    abort(http_codes.HTTP_FORBIDDEN_403, error_message=OBJECT_EDIT_NOT_ALLOWED.format("comment"))

                data = parser.parse_args()
                data["comment_modified_at"] = datetime.utcnow().isoformat()
                data = {key: value for key, value in data.items() if value}

                old_image_file = comment.comment_image
                new_image_file = data["comment_image"]

                updated_comment = self.comment_update_schema.load(data)
                async_tasks = []

                for key, value in updated_comment.items():
                    setattr(comment, key, value)

                if new_image_file:
                    if old_image_file:
                        db.session.delete(old_image_file)

                    db.session.add(comment.comment_image)
                    task = save_file(new_image_file, comment.comment_image.file_url[1:])
                    async_tasks.append(task)

                await asyncio.gather(*async_tasks)

            return jsonify(self.comment_get_schema.dump(comment))
        except ValidationError as e:
            abort(http_codes.HTTP_BAD_REQUEST_400, error_message=str(e))
