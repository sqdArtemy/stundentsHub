import http_codes
from sqlalchemy import text
from flask_restful import Resource, abort, reqparse
from werkzeug.datastructures import FileStorage
from datetime import datetime
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify, make_response
from models import Post, User
from db_init import db
from schemas import PostGetSchema, PostCreateSchema, PostUpdateSchema
from text_templates import OBJECT_DOES_NOT_EXIST, OBJECT_DELETED, OBJECT_EDIT_NOT_ALLOWED, OBJECT_DELETE_NOT_ALLOWED
from utilities import is_authorized_error_handler, save_file

parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument("post_heading", location="form")
parser.add_argument("post_text", location="form")
parser.add_argument("post_image", type=FileStorage, location="files")
parser.add_argument("post_files", type=FileStorage, location="files", action="append")


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

        image_file = data.get("post_image")
        files = data.get("post_files")

        try:
            post = self.post_create_schema.load(data)
            post.create()

            if image_file:
                post.post_image.create()
                save_file(image_file, post.post_image.file_url[1:])

            if files:
                file_count = 0
                for file in files:
                    save_file(file, post.post_files[file_count].file_url[1:])
                    file_count += 1

                db.session.add_all(post.post_files)
                db.session.commit()

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

        image_file = data.get("post_image")
        files = data.get("post_files")

        try:
            updated_post = self.post_update_schema.load(data)
            for key, value in updated_post.items():
                setattr(post, key, value)
            post.save_changes()

            if image_file:
                post.post_image.create()
                save_file(image_file, post.post_image.file_url[1:])

            if files:
                file_count = 0
                for file in files:
                    save_file(file, post.post_files[file_count].file_url[1:])
                    file_count += 1

                db.session.add_all(post.post_files)
                db.session.commit()

            return jsonify(self.post_get_schema.dump(post))
        except ValidationError as e:
            abort(http_codes.HTTP_BAD_REQUEST_400, error_message=str(e))


class PostRateView(Resource):
    post_get_schema = PostGetSchema()

    @is_authorized_error_handler()
    @jwt_required()
    def put(self, post_id):
        user = User.query.get(get_jwt_identity())
        post = Post.query.get(post_id)
        if not post:
            abort(http_codes.HTTP_BAD_REQUEST_400, error_message=OBJECT_DOES_NOT_EXIST.format("Post", post_id))

        rate_parser = reqparse.RequestParser(bundle_errors=True)
        rate_parser.add_argument("likes", type=bool, location="form")
        rate_parser.add_argument("dislikes", type=bool, location="form")
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
                )
                UPDATE posts
                SET
                    post_likes = (SELECT count_likes FROM likes_count),
                    post_dislikes = (SELECT count_dislikes FROM dislikes_count),
                    post_rating = ROUND(
                        (
                            COALESCE((SELECT count_likes FROM likes_count), 0) * 100 /
                            (
                                COALESCE((SELECT count_likes FROM likes_count), 0) +
                                COALESCE((SELECT count_dislikes FROM dislikes_count), 0)
                            )
                        ), 2
                    )
                WHERE post_id = :post_id
                """),
            {"post_id": post_id}
        )
        post.save_changes()

        return jsonify(self.post_get_schema.dump(post))
