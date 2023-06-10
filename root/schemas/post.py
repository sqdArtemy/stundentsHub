from marshmallow import fields, validate, validates, ValidationError, EXCLUDE, pre_load
from .comment import CommentGetSchema
from .user import UserGetSchema
from .file import FileCreateSchema, FileGetSchema
from models import Post, User
from app_init import ma
from utilities import instance_exists_by_id
from text_templates import OBJECT_DOES_NOT_EXIST


class PostSchemaMixin:
    post_heading = fields.Str(required=False, validate=validate.Length(min=10, max=100))
    post_text = fields.Str(required=False, validate=validate.Length(min=10, max=2500))
    post_created_at = fields.DateTime(required=False)
    post_modified_at = fields.DateTime(required=False)
    post_author = fields.Integer(required=False)
    post_image = fields.Nested(FileCreateSchema(), allow_none=True)
    post_files = fields.List(fields.Nested(FileCreateSchema()), allow_none=True)

    @pre_load
    def serialize_data(self, data, **kwargs):
        image_file = data.get("post_image")
        files = data.get("post_files")

        if image_file:
            data["post_image"] = {"file_raw": image_file}

        if files:
            data["post_files"] = [{"file_raw": file} for file in files]

        return data

    @validates("post_author")
    def validate_post_author(self, value):
        if not instance_exists_by_id(_id=value, model=User):
            raise ValidationError(OBJECT_DOES_NOT_EXIST.format("Post", value))


class PostGetSchema(ma.SQLAlchemyAutoSchema):
    post_comments = fields.Nested(CommentGetSchema(), many=True)
    author = fields.Nested(UserGetSchema(only=("user_id", "user_name", "user_surname")), data_key="post_author")
    post_image = fields.Nested(FileGetSchema())
    post_files = fields.List(fields.Nested(FileGetSchema()))

    class Meta:
        model = Post
        ordered = True
        fields = ("post_id", "post_heading", "post_text", "post_rating", "post_image", "post_likes", "post_dislikes",
                  "post_created_at", "post_modified_at", "author", "post_comments", "post_files")
        include_relationships = True
        load_instance = True
        include_fk = True
        unknown = EXCLUDE


class PostCreateSchema(ma.SQLAlchemyAutoSchema, PostSchemaMixin):
    post_heading = fields.Str(required=True, validate=validate.Length(min=10, max=100))
    post_text = fields.Str(required=True, validate=validate.Length(min=10, max=2500))
    post_created_at = fields.DateTime(required=True)
    post_author = fields.Integer(required=True)

    class Meta:
        model = Post
        fields = ("post_heading", "post_text", "post_image", "post_created_at", "post_modified_at",
                  "post_author", "post_files")
        include_relationships = True
        load_instance = True
        unknown = EXCLUDE


class PostUpdateSchema(ma.SQLAlchemyAutoSchema, PostSchemaMixin):
    class Meta:
        model = Post
        ordered = True
        fields = ("post_heading", "post_image", "post_text", "post_modified_at", "post_files")
        include_relationships = True
        load_instance = False
        unknown = EXCLUDE
