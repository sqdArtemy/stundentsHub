import http_codes
import asyncio
from sqlalchemy.orm import joinedload
from sqlalchemy import text
from flask_restful import Resource, abort, reqparse
from werkzeug.datastructures import FileStorage
from datetime import datetime
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify, make_response
from models import Post, User, File, Notification
from db_init import db
from schemas import PostGetSchema, PostCreateSchema, PostUpdateSchema, FileCreateSchema
from text_templates import OBJECT_DOES_NOT_EXIST, OBJECT_DELETED, OBJECT_EDIT_NOT_ALLOWED, OBJECT_DELETE_NOT_ALLOWED
from utilities import is_authorized_error_handler, save_file, delete_file
from .mixins import PaginationMixin, FilterMixin, SortMixin
from .technical import sort_filter_parser

parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument("post_heading", location="form")
parser.add_argument("post_text", location="form")
parser.add_argument("post_image", type=FileStorage, location="files")


class PostListView(Resource, PaginationMixin, FilterMixin, SortMixin):
    posts_get_schema = PostGetSchema(many=True)
    post_get_schema = PostGetSchema()
    post_create_schema = PostCreateSchema()

    @is_authorized_error_handler()
    @jwt_required()
    def get(self):
        data = sort_filter_parser.parse_args()
        sort_by = data.get("sort_by")
        filters = data.get("filters")

        posts_query = Post.query.options(joinedload(Post.author))

        try:
            if filters:
                filter_mappings = {"post_author": (Post.author, User.user_id)}
                posts_query = self.get_filtered_query(
                    query=posts_query,
                    model=Post,
                    filters=filters,
                    filter_mappings=filter_mappings
                )

            if sort_by:
                sort_mappings = {"post_author": (User, User.user_id)}
                posts_query = self.get_sorted_query(
                    query=posts_query,
                    model=Post,
                    sort_fields=sort_by,
                    sort_mappings=sort_mappings
                )
            else:
                posts_query = posts_query.order_by(Post.post_id)

        except AttributeError as e:
            abort(http_codes.HTTP_BAD_REQUEST_400, error_message=str(e))

        response = self.get_paginated_response(
            query=posts_query,
            items_schema=self.posts_get_schema,
            model_plural_name="posts",
            count_field_name="post_count"
        )

        return response

    @is_authorized_error_handler()
    @jwt_required()
    async def post(self):
        parser.add_argument("post_files", type=FileStorage, location="files", action="append")
        data = parser.parse_args()

        data["post_author"] = get_jwt_identity()
        data["post_created_at"] = datetime.utcnow().isoformat()

        image_file = data.get("post_image")
        files = data.get("post_files")

        try:
            with db.session.begin():
                post = self.post_create_schema.load(data)
                db.session.add(post)
                async_tasks = []

                if image_file:
                    db.session.add(post.post_image)
                    task = save_file(image_file, post.post_image.file_url[1:])
                    async_tasks.append(task)

                if files:
                    for index, file in enumerate(files):
                        task = save_file(file, post.post_files[index].file_url[1:])
                        async_tasks.append(task)

                    db.session.add_all(post.post_files)
                await asyncio.gather(*async_tasks)

            return make_response(jsonify(self.post_get_schema.dump(post)), http_codes.HTTP_CREATED_201)
        except ValidationError as e:
            abort(http_codes.HTTP_BAD_REQUEST_400, error_message=str(e))


class PostDetailedView(Resource):
    post_get_schema = PostGetSchema()
    post_update_schema = PostUpdateSchema()

    @is_authorized_error_handler()
    @jwt_required()
    def get(self, post_id: int):
        post = Post.query.get_or_404(post_id, description=OBJECT_DOES_NOT_EXIST.format("Post", post_id))

        return jsonify(self.post_get_schema.dump(post))

    @classmethod
    @is_authorized_error_handler()
    @jwt_required()
    async def delete(cls, post_id: int):
        post = Post.query.get_or_404(post_id, description=OBJECT_DOES_NOT_EXIST.format("Post", post_id))

        editor = User.query.get(get_jwt_identity())
        if editor is not post.author:
            abort(http_codes.HTTP_FORBIDDEN_403, error_message=OBJECT_DELETE_NOT_ALLOWED.format("post"))

        post.delete()

        return {"success": OBJECT_DELETED.format("Post", post_id)}, http_codes.HTTP_NO_CONTENT_204

    @is_authorized_error_handler()
    @jwt_required()
    async def put(self, post_id: int):
        try:
            with db.session.begin():
                post = Post.query.get_or_404(post_id, description=OBJECT_DOES_NOT_EXIST.format("Post", post_id))

                editor = User.query.get(get_jwt_identity())
                if editor is not post.author:
                    abort(http_codes.HTTP_FORBIDDEN_403, error_message=OBJECT_EDIT_NOT_ALLOWED.format("post"))

                data = parser.parse_args()
                data["post_modified_at"] = datetime.utcnow().isoformat()
                data = {key: value for key, value in data.items() if value}

                old_image_file = post.post_image
                new_image_file = data.get("post_image")

                async_tasks = []

                updated_post = self.post_update_schema.load(data)
                for key, value in updated_post.items():
                    setattr(post, key, value)

                if new_image_file:
                    if old_image_file:
                        task = delete_file(old_image_file.file_url[1:])
                        async_tasks.append(task)
                        db.session.delete(old_image_file)

                    db.session.add(post.post_image)
                    task = save_file(new_image_file, post.post_image.file_url[1:])
                    async_tasks.append(task)

                await asyncio.gather(*async_tasks)

            return jsonify(self.post_get_schema.dump(post))
        except ValidationError as e:
            abort(http_codes.HTTP_BAD_REQUEST_400, error_message=str(e))


class PostRateView(Resource):
    post_get_schema = PostGetSchema()

    @is_authorized_error_handler()
    @jwt_required()
    def put(self, post_id):
        user = User.query.get(get_jwt_identity())
        post = Post.query.get_or_404(post_id, description=OBJECT_DOES_NOT_EXIST.format("Post", post_id))

        rate_parser = reqparse.RequestParser(bundle_errors=True)
        rate_parser.add_argument("likes", type=bool, location="form", required=True)
        rate_parser.add_argument("dislikes", type=bool, location="form", required=True)
        data = rate_parser.parse_args()

        if data["likes"] is True and data["dislikes"] is True:
            abort(http_codes.HTTP_BAD_REQUEST_400, error_message="You can only like, or dislike post, not both!")

        users_liked = post.post_liked_by
        users_disliked = post.post_disliked_by

        if data["likes"] is True:
            if user in users_liked:
                abort(http_codes.HTTP_BAD_REQUEST_400, error_message="You already liked this post!")

            if user in users_disliked:
                users_disliked.remove(user)

            users_liked.append(user)

        if data["dislikes"] is True:
            if user in users_disliked:
                abort(http_codes.HTTP_BAD_REQUEST_400, error_message="You already disliked this post!")

            if user in users_liked:
                users_liked.remove(user)

            users_disliked.append(user)

        post.post_liked_by = users_liked
        post.post_disliked_by = users_disliked
        post.save_changes()

        db.session.execute(
            text("""
                WITH likes_count AS (
                    SELECT COUNT(*) AS count_likes
                    FROM user_likes_post
                    WHERE post_id = :post_id
                ),
                dislikes_count AS (
                    SELECT COUNT(*) AS count_dislikes
                    FROM user_dislikes_post
                    WHERE post_id = :post_id
                ),
                ratings AS (
                    SELECT
                        COALESCE((SELECT count_likes FROM likes_count), 0) AS likes,
                        COALESCE((SELECT count_dislikes FROM dislikes_count), 0) AS dislikes
                )
                UPDATE posts
                SET
                    post_likes = (SELECT likes FROM ratings),
                    post_dislikes = (SELECT dislikes FROM ratings),
                    post_rating = CASE
                        WHEN ((SELECT likes FROM ratings) + (SELECT dislikes FROM ratings)) = 0 THEN 0.0
                        ELSE ROUND((SELECT likes FROM ratings) * 100 / ((SELECT likes FROM ratings) + (SELECT dislikes FROM ratings)), 2)
                    END
                WHERE post_id = :post_id
            """),
            {"post_id": post_id}
        )

        action = "liked" if data.get("likes") else "disliked" if data.get("dislikes") else ""
        notification = Notification(
            notification_text=f"Your post {post} have been {action} by {user}.",
            notification_receiver=post.author,
            notification_sender_url=f"/user/{user.user_id}"
        )
        notification.create()

        post.save_changes()

        return jsonify(self.post_get_schema.dump(post))


class PostAddFile(Resource):
    post_get_schema = PostGetSchema()

    @is_authorized_error_handler()
    @jwt_required()
    async def post(self, post_id):
        try:
            with db.session.begin():
                post = Post.query.get_or_404(post_id, description=OBJECT_DOES_NOT_EXIST.format("Post", post_id))

                editor = User.query.get(get_jwt_identity())
                if editor is not post.author:
                    abort(http_codes.HTTP_FORBIDDEN_403, error_message=OBJECT_EDIT_NOT_ALLOWED.format("Post"))

                file_add_parser = reqparse.RequestParser(bundle_errors=True)
                file_add_parser.add_argument("file", type=FileStorage, location="files", required=True)
                data = file_add_parser.parse_args()

                file = data["file"]
                file_model = FileCreateSchema().load({"file_raw": file})

                await asyncio.gather(*[save_file(file, file_model.file_url[1:])])
                db.session.add(file_model)

                post.post_files.append(file_model)

            return jsonify(self.post_get_schema.dump(post))
        except ValidationError as e:
            abort(http_codes.HTTP_BAD_REQUEST_400, error_message=str(e))


class PostDeleteFile(Resource):
    post_get_schema = PostGetSchema()

    @is_authorized_error_handler()
    @jwt_required()
    async def delete(self, post_id, file_id):
        try:
            with db.session.begin():
                post = Post.query.get_or_404(post_id, description=OBJECT_DOES_NOT_EXIST.format("Post", post_id))
                file = File.query.get_or_404(file_id, description=OBJECT_DOES_NOT_EXIST.format("File", file_id))

                editor = User.query.get(get_jwt_identity())
                if editor is not post.author:
                    abort(http_codes.HTTP_FORBIDDEN_403, error_message=OBJECT_EDIT_NOT_ALLOWED.format("Post"))

                if file not in post.post_files:
                    abort(
                        http_codes.HTTP_BAD_REQUEST_400,
                        error_message=f"File {file.file_name} is not in a post with id {post_id}."
                    )

                post.post_files.remove(file)
                db.session.delete(file)

            return jsonify(self.post_get_schema.dump(post))

        except ValidationError as e:
            abort(http_codes.HTTP_BAD_REQUEST_400, error_message=str(e))


class PostBulkEditFiles(Resource):
    post_get_schema = PostGetSchema()

    @is_authorized_error_handler()
    @jwt_required()
    async def post(self, post_id):
        try:
            with db.session.begin():
                post = Post.query.get_or_404(post_id, description=OBJECT_DOES_NOT_EXIST.format("Post", post_id))

                editor = User.query.get(get_jwt_identity())
                if editor is not post.author:
                    abort(http_codes.HTTP_FORBIDDEN_403, error_message=OBJECT_EDIT_NOT_ALLOWED.format("Post"))

                files_bulk_add_parser = reqparse.RequestParser()
                files_bulk_add_parser.add_argument(
                    "files", type=FileStorage, location="files",
                    action="append", required=True
                )
                data = files_bulk_add_parser.parse_args()

                files = data["files"]
                files_models = [FileCreateSchema().load({"file_raw": file}) for file in files]
                async_tasks = []

                for index, file in enumerate(files):
                    task = save_file(file, files_models[index].file_url[1:])
                    async_tasks.append(task)

                db.session.add_all(files_models)
                post.post_files.extend(files_models)

                await asyncio.gather(*async_tasks)

            return jsonify(self.post_get_schema.dump(post))
        except ValidationError as e:
            abort(http_codes.HTTP_BAD_REQUEST_400, error_message=str(e))

    @is_authorized_error_handler()
    @jwt_required()
    async def delete(self, post_id):
        try:
            with db.session.begin():
                post = Post.query.get_or_404(post_id, description=OBJECT_DOES_NOT_EXIST.format("Post", post_id))

                file_bulk_delete_parser = reqparse.RequestParser()
                file_bulk_delete_parser.add_argument("files", type=int, action="append", required=True, location="form")
                data = file_bulk_delete_parser.parse_args()

                file_ids_to_delete = set(data["files"])
                post_file_ids = {file.file_id for file in post.post_files}
                if not file_ids_to_delete.issubset(post_file_ids):
                    abort(
                        http_codes.HTTP_BAD_REQUEST_400,
                        error_message=f"Post with id:"
                                      f" {post_id} does not have files with ids:{file_ids_to_delete-post_file_ids}"
                    )

                deleted_objects = [file for file in post.post_files if file.file_id in file_ids_to_delete]
                post.post_files = [file for file in post.post_files if file.file_id not in file_ids_to_delete]

                for file in deleted_objects:
                    db.session.delete(file)

                return jsonify(self.post_get_schema.dump(post))
        except ValidationError as e:
            abort(http_codes.HTTP_BAD_REQUEST_400, error_message=str(e))
