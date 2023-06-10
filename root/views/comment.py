import http_codes
from flask_restful import Resource, abort, reqparse
from werkzeug.datastructures import FileStorage
from datetime import datetime
from marshmallow import ValidationError
from flask import jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Comment, User
from schemas import CommentGetSchema, CommentCreateSchema, CommentUpdateSchema, UserGetSchema
from text_templates import OBJECT_DOES_NOT_EXIST, OBJECT_DELETED, OBJECT_EDIT_NOT_ALLOWED, OBJECT_DELETE_NOT_ALLOWED
from utilities import is_authorized_error_handler, save_file

parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument("comment_text", location="form")
parser.add_argument("comment_image", type=FileStorage, location="files")


class CommentListView(Resource):
    comments_get_schema = CommentGetSchema(many=True)
    comment_get_schema = CommentGetSchema()
    comment_create_schema = CommentCreateSchema()

    @is_authorized_error_handler()
    @jwt_required()
    def get(self):
        comments = Comment.query.all()
        return jsonify(self.comments_get_schema.dump(comments))

    @is_authorized_error_handler()
    @jwt_required()
    def post(self):
        parser_post = parser.copy()
        parser_post.add_argument("comment_post", type=int, location="form")
        parser_post.add_argument("comment_parent", type=int, location="form")
        data = parser_post.parse_args()

        data["comment_author"] = UserGetSchema(only=("user_id",)).dump(User.query.get(get_jwt_identity()))
        data["comment_created_at"] = str(datetime.utcnow())
        image_file = data["comment_image"]

        try:
            comment = self.comment_create_schema.load(data)

            if comment.comment_parent and comment.comment_post != comment.parent_comment.comment_post:
                abort(http_codes.HTTP_FORBIDDEN_403, error_message="Parent comment has different post.")

            comment.create()

            if image_file:
                comment.comment_image.create()
                save_file(image_file, comment.comment_image.file_url[1:])

            return make_response(jsonify(self.comment_get_schema.dump(comment)), http_codes.HTTP_CREATED_201)
        except ValidationError as e:
            abort(http_codes.HTTP_BAD_REQUEST_400, error_message=str(e))


class CommentDetailedView(Resource):
    comment_get_schema = CommentGetSchema()
    comment_update_schema = CommentUpdateSchema()

    @is_authorized_error_handler()
    @jwt_required()
    def get(self, comment_id):
        comment = Comment.query.get(comment_id)
        if not comment:
            abort(http_codes.HTTP_NOT_FOUND_404, error_message=OBJECT_DOES_NOT_EXIST.format("Comment", comment_id))

        return jsonify(self.comment_get_schema.dump(comment))

    @classmethod
    @is_authorized_error_handler()
    @jwt_required()
    def delete(cls, comment_id):
        comment = Comment.query.get(comment_id)
        if not comment:
            abort(http_codes.HTTP_NOT_FOUND_404, error_message=OBJECT_DOES_NOT_EXIST.format("Comment", comment_id))

        editor = User.query.get(get_jwt_identity())
        if editor is not comment.author:
            abort(http_codes.HTTP_FORBIDDEN_403, error_message=OBJECT_DELETE_NOT_ALLOWED.format("comment"))

        comment.delete()

        return {"success": OBJECT_DELETED.format("Comment", comment_id)}, http_codes.HTTP_NO_CONTENT_204

    @is_authorized_error_handler()
    @jwt_required()
    def put(self, comment_id):
        comment = Comment.query.get(comment_id)
        if not comment:
            abort(http_codes.HTTP_NOT_FOUND_404, error_message=OBJECT_DOES_NOT_EXIST.format("Comment", comment_id))

        editor = User.query.get(get_jwt_identity())
        if editor is not comment.author:
            abort(http_codes.HTTP_FORBIDDEN_403, error_message=OBJECT_EDIT_NOT_ALLOWED.format("comment"))

        data = parser.parse_args()
        data["comment_modified_at"] = str(datetime.utcnow())
        data = {key: value for key, value in data.items() if value}
        image_file = data["comment_image"]

        try:
            updated_comment = self.comment_update_schema.load(data)
            for key, value in updated_comment.items():
                setattr(comment, key, value)

            comment.save_changes()
            if image_file:
                comment.comment_image.create()
                save_file(image_file, comment.comment_image.file_url[1:])

            return jsonify(self.comment_get_schema.dump(comment))
        except ValidationError as e:
            abort(http_codes.HTTP_BAD_REQUEST_400, error_message=str(e))
