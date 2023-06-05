from marshmallow import fields, validate, validates, ValidationError, EXCLUDE
from models import User, Comment, Post
from app_init import ma
from .user import UserGetSchema
from checkers import instance_exists_by_id
from text_templates import OBJECT_DOES_NOT_EXIST
from db_init import db


class CommentSchemaMixin:
    comment_text = fields.Str(required=False, validate=validate.Length(min=1, max=250))
    comment_created_at = fields.DateTime(required=False)
    comment_modified_at = fields.DateTime(required=False)
    comment_author = fields.Integer(required=True)
    comment_post = fields.Integer(required=False)

    @validates("comment_author")
    def validate_comment_author(self, value):
        if not instance_exists_by_id(_id=value, model=User):
            raise ValidationError(OBJECT_DOES_NOT_EXIST.format("User", value))

    @validates("comment_post")
    def validate_comment_post(self, value):
        if not instance_exists_by_id(_id=value, model=Post):
            raise ValidationError(OBJECT_DOES_NOT_EXIST.format("Post", value))

    @validates("comment_parent")
    def validate_comment_parent(self, value):
        if not instance_exists_by_id(_id=value, model=Comment):
            raise ValidationError(OBJECT_DOES_NOT_EXIST.format("Comment", value))


class CommentGetSchema(ma.SQLAlchemyAutoSchema):
    author = fields.Nested(UserGetSchema(only=("user_id", "user_name", "user_surname")), data_key="comment_author")
    parent_comment = fields.Nested("CommentGetSchema", data_key="comment_parent",
                                   exclude=("parent_comment", "comment_post"))
    comment_parent = fields.Integer(allow_none=True)

    class Meta:
        model = Comment
        ordered = True
        fields = ("comment_id", "comment_text", "comment_created_at",
                  "comment_modified_at", "author", "comment_post", "parent_comment")
        include_relationships = True
        load_instance = True
        include_fk = True
        sqla_session = db.session
        unknown = EXCLUDE


class CommentCreateSchema(ma.SQLAlchemyAutoSchema, CommentSchemaMixin):
    comment_text = fields.Str(required=True, validate=validate.Length(min=1, max=250))
    comment_created_at = fields.DateTime(required=True)
    comment_post = fields.Integer(required=False)
    author = fields.Nested(UserGetSchema(only=("user_id",)), data_key="comment_author")
    parent_comment = fields.Nested("CommentCreateSchema", data_key="comment_parent", allow_none=True)
    comment_parent = fields.Integer(allow_none=True)

    class Meta:
        model = Comment
        fields = ("comment_id", "comment_text", "comment_created_at", "comment_modified_at", "author",
                  "comment_post", "parent_comment")
        include_relationships = True
        load_instance = True
        include_fk = True
        sqla_session = db.session
        unknown = EXCLUDE


class CommentUpdateSchema(ma.SQLAlchemyAutoSchema, CommentSchemaMixin):
    class Meta:
        model = Comment
        ordered = True
        fields = ("comment_text", "comment_modified_at")
        include_relationships = True
        load_instance = False
        unknown = EXCLUDE
