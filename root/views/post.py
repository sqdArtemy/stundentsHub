import http_codes
from flask_restful import Resource, abort, reqparse
from datetime import datetime
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify, make_response
from models import Post, User
from schemas import PostGetSchema, PostCreateSchema, PostUpdateSchema
from text_templates import OBJECT_DOES_NOT_EXIST, OBJECT_DELETED, OBJECT_EDIT_NOT_ALLOWED, OBJECT_DELETE_NOT_ALLOWED
from checkers import is_authorized_error_handler

parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument("post_heading", location="form")
parser.add_argument("post_text", location="form")


class PostListView(Resource):
    posts_get_schema = PostGetSchema(many=True)
    post_get_schema = PostGetSchema()
    post_create_schema = PostCreateSchema()

    @is_authorized_error_handler()
    @jwt_required()
    def get(self):
        posts = Post.query.all()
        return jsonify(self.posts_get_schema.dump(posts))

    @is_authorized_error_handler()
    @jwt_required()
    def post(self):
        data = parser.parse_args()
        data["post_author"] = get_jwt_identity()
        data["post_created_at"] = str(datetime.utcnow())

        try:
            post = self.post_create_schema.load(data)
            post.create()

            return make_response(jsonify(self.post_get_schema.dump(post)), http_codes.HTTP_CREATED_201)
        except ValidationError as e:
            abort(http_codes.HTTP_BAD_REQUEST_400, error_message=str(e))


class PostDetailedView(Resource):
    post_get_schema = PostGetSchema()
    post_update_schema = PostUpdateSchema()

    @is_authorized_error_handler()
    @jwt_required()
    def get(self, post_id: int):
        post = Post.query.get(post_id)
        if not post:
            abort(http_codes.HTTP_NOT_FOUND_404, error_message=OBJECT_DOES_NOT_EXIST.format("Post", post_id))

        return jsonify(self.post_get_schema.dump(post))

    @classmethod
    @is_authorized_error_handler()
    @jwt_required()
    def delete(cls, post_id: int):
        post = Post.query.get(post_id)
        if not post:
            abort(http_codes.HTTP_NOT_FOUND_404, error_message=OBJECT_DOES_NOT_EXIST.format("Post", post_id))

        editor = User.query.get(get_jwt_identity())
        if editor is not post.author:
            abort(http_codes.HTTP_FORBIDDEN_403, error_message=OBJECT_DELETE_NOT_ALLOWED.format("post"))

        post.delete()

        return {"success": OBJECT_DELETED.format("Post", post_id)}, http_codes.HTTP_NO_CONTENT_204

    @is_authorized_error_handler()
    @jwt_required()
    def put(self, post_id: int):
        post = Post.query.get(post_id)
        if not post:
            abort(http_codes.HTTP_NOT_FOUND_404, error_message=OBJECT_DOES_NOT_EXIST.format("Post", post_id))

        editor = User.query.get(get_jwt_identity())
        if editor is not post.author:
            abort(http_codes.HTTP_FORBIDDEN_403, error_message=OBJECT_EDIT_NOT_ALLOWED.format("post"))

        data = parser.parse_args()
        data["post_modified_at"] = str(datetime.utcnow())
        data = {key: value for key, value in data.items() if value}

        try:
            updated_post = self.post_update_schema.load(data)
            for key, value in updated_post.items():
                setattr(post, key, value)
            post.save_changes()

            return jsonify(self.post_get_schema.dump(post))
        except ValidationError as e:
            abort(http_codes.HTTP_BAD_REQUEST_400, error_message=str(e))
