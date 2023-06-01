from flask_restful import Resource, abort
from datetime import datetime
from marshmallow import ValidationError
from flask import jsonify, make_response
from models import Post
from schemas import PostGetSchema, PostCreateSchema, PostUpdateSchema
from app import db, parser
from text_templates import MSG_MISSING, OBJECT_DOES_NOT_EXIST, OBJECT_DELETED
from checkers import instance_exists


class PostListView(Resource):
    posts_get_schema = PostGetSchema(many=True)
    post_get_schema = PostGetSchema()
    post_create_schema = PostCreateSchema()

    def get(self):
        posts = Post.query.all()
        return jsonify(self.posts_get_schema.dump(posts))

    def post(self):
        parser.add_argument("post_heading", location="form")
        parser.add_argument("post_text", location="form")
        parser.add_argument("post_author", location="form")
        data = parser.parse_args()
        data["post_created_at"] = datetime.utcnow()
        data["post_modified_at"] = None

        try:
            post = self.post_create_schema.load(data)
            post.create()

            return make_response(jsonify(self.post_get_schema.dump(post)), 201)
        except ValidationError as e:
            abort(400, error_message=e)


class PostDetailedView(Resource):
    post_get_schema = PostGetSchema()
    post_update_schema = PostUpdateSchema()

    def get(self, post_id: int):
        post = Post.query.get(post_id)
        if not instance_exists(post):
            abort(404, error_message=OBJECT_DOES_NOT_EXIST.format("Post", post_id))
        return jsonify(self.post_get_schema.dump(post))

    @classmethod
    def delete(cls, post_id: int):
        post = Post.query.get(post_id)
        if not instance_exists(post):
            abort(404, error_message=OBJECT_DOES_NOT_EXIST.format("Post", post_id))
        post.delete()

        return {"success": OBJECT_DELETED.format("Post", post_id)}, 200

    def update(self, post_id: int):
        post = Post.query.get(post_id)
        if not instance_exists(post):
            abort(404, error_message=OBJECT_DOES_NOT_EXIST.format("Post", post_id))

        parser.add_argument("post_heading", location="form")
        parser.add_argument("post_text", location="form")
        data = parser.parse_args()
        data["post_modified_at"] = datetime.utcnow()
        data = {key: value for key, value in data.items() if value}

        try:
            updated_post = self.post_update_schema.load(data)
            for key, value in updated_post.items():
                setattr(post, key, value)
            post.save_changes()

            return jsonify(self.post_get_schema.dump(post))
        except ValidationError as e:
            abort(404, error_message=e)
