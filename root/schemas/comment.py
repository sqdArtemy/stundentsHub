from marshmallow import fields, validate, validates, ValidationError, EXCLUDE, pre_load
from models import User, Comment, Post
from app_init import ma
from schemas.user import UserGetSchema
from schemas.file import FileCreateSchema, FileGetSchema
from utilities import instance_exists_by_id
from text_templates import OBJECT_DOES_NOT_EXIST
from db_init import db


class CommentSchemaMixin:
    comment_author = fields.Integer(required=True)
    comment_post = fields.Integer(required=True)
    comment_image = fields.Nested(FileCreateSchema(), allow_none=True)

    @pre_load
    def serialize_data(self, data, **kwargs):
        image_file = data.get("comment_image")

        if data.get("comment_parent"):
            data["comment_parent"] = CommentGetSchema().dump(Comment.query.get(data["comment_parent"]))

        if image_file:
            data["comment_image"] = {"file_raw": image_file}

        return data

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
    parent_comment = fields.Nested("self", data_key="comment_parent",
                                   exclude=("parent_comment", "comment_post"))
    comment_image = fields.Nested(FileGetSchema(), allow_none=True)

    class Meta:
        model = Comment
        ordered = True
        fields = ("comment_id", "comment_text", "comment_image", "comment_created_at",
                  "comment_modified_at", "author", "comment_post", "parent_comment")
        include_relationships = True
        load_instance = True
        include_fk = True
        sqla_session = db.session
        unknown = EXCLUDE


class CommentCreateSchema(ma.SQLAlchemyAutoSchema, CommentSchemaMixin):
    comment_text = fields.Str(required=True, validate=validate.Length(min=1, max=250))
    comment_created_at = fields.DateTime(required=True)
    author = fields.Nested(UserGetSchema(only=("user_id",)), data_key="comment_author")
    parent_comment = fields.Nested(CommentGetSchema(exclude=("parent_comment", "comment_post")),
                                   data_key="comment_parent", allow_none=True)

    class Meta:
        model = Comment
        fields = ("comment_id", "comment_text", "comment_image", "comment_created_at", "comment_modified_at", "author",
                  "comment_post", "parent_comment")
        include_relationships = True
        load_instance = True
        include_fk = True
        ordered = True
        sqla_session = db.session
        unknown = EXCLUDE


class CommentUpdateSchema(ma.SQLAlchemyAutoSchema, CommentSchemaMixin):
    comment_text = fields.Str(required=False, validate=validate.Length(min=1, max=250))

    class Meta:
        model = Comment
        ordered = True
        fields = ("comment_text", "comment_image", "comment_modified_at")
        include_relationships = True
        load_instance = False
        include_fk = True
        sqla_session = db.session
        unknown = EXCLUDE
