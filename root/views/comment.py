from flask_restful import Resource, abort
from datetime import datetime
from marshmallow import ValidationError
from flask import jsonify, make_response
from flask_jwt_extended import jwt_required
from models import Comment
from schemas import CommentGetSchema, CommentCreateSchema, CommentUpdateSchema
from app_init import parser
from text_templates import OBJECT_DOES_NOT_EXIST, OBJECT_DELETED
from checkers import instance_exists, is_authorized_error_handler


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
        parser.add_argument("comment_text", location="form")
        parser.add_argument("comment_author", location="form")
        parser.add_argument("comment_post", location="form")
        data = parser.parse_args()
        data["comment_created_at"] = datetime.utcnow()
        data["comment_modified_at"] = None

        try:
            comment = self.comment_create_schema.load(data)
            comment.create()

            return make_response(jsonify(self.comment_get_schema.dump(comment)),201)
        except ValidationError as e:
            abort(400, error_message=str(e))


class CommentDetailedView(Resource):
    comment_get_schema = CommentGetSchema()
    comment_update_schema = CommentUpdateSchema()

    @is_authorized_error_handler()
    @jwt_required()
    def get(self, comment_id):
        comment = Comment.query.get(comment_id)
        if not instance_exists(comment):
            abort(404, error_message=OBJECT_DOES_NOT_EXIST.format("Comment", comment_id))

        return jsonify(self.comment_get_schema.dump(comment))

    @classmethod
    @is_authorized_error_handler()
    @jwt_required()
    def delete(cls, comment_id):
        comment = Comment.query.get(comment_id)
        if not instance_exists(comment):
            abort(404, error_message=OBJECT_DOES_NOT_EXIST.format("Comment", comment_id))
        comment.delete()

        return {"success": OBJECT_DELETED.format("Comment", comment_id)}

    @is_authorized_error_handler()
    @jwt_required()
    def put(self, comment_id):
        comment = Comment.query.get(comment_id)
        if not instance_exists(comment):
            abort(404, error_message=OBJECT_DOES_NOT_EXIST.format("Comment", comment_id))

        parser.add_argument("comment_text")
        data = parser.parse_args()
        data["comment_modified_at"] = datetime.utcnow()
        data = {key: value for key,value in data.items() if value}

        try:
            updated_comment = self.comment_update_schema.load(data)
            for key, value in updated_comment.items:
                setattr(comment, key, value)
            comment.save_changes()

            return jsonify(self.comment_get_schema.dump(comment))
        except ValidationError as e:
            abort(400, error_message=str(e))
