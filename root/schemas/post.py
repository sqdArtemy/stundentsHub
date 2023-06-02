from marshmallow import fields, validate, validates, ValidationError
from models import Post, User
from app_init import ma
from checkers import instance_exists_by_id
from text_templates import OBJECT_DOES_NOT_EXIST


class PostSchemaMixin:
    post_heading = fields.Str(required=False, validate=validate.Length(min=10, max=100))
    post_text = fields.Str(required=False, validate=validate.Length(min=10, max=2500))
    post_created_at = fields.DateTime(required=False)
    post_modified_at = fields.DateTime(required=False)
    post_author = fields.Integer(required=False)

    @validates("post_author")
    def validate_post_author(self, value):
        if not instance_exists_by_id(_id=value, model=User):
            raise ValidationError(OBJECT_DOES_NOT_EXIST.format("Post", value))


class PostGetSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Post
        ordered = True
        fields = ("post_id", "post_heading", "post_text", "post_created_at", "post_modified_at",
                  "post_author", "post_comments")
        include_relationships = True
        load_instance = True


class PostCreateSchema(ma.SQLAlchemyAutoSchema, PostSchemaMixin):
    post_heading = fields.Str(required=True, validate=validate.Length(min=10, max=100))
    post_text = fields.Str(required=True, validate=validate.Length(min=10, max=2500))
    post_created_at = fields.DateTime(required=True)
    post_modified_at = fields.DateTime(required=True)
    post_author = fields.Integer(required=True)

    class Meta:
        model = Post
        ordered = True
        fields = ("post_heading", "post_text", "post_created_at", "post_modified_at", "post_author")
        include_relationships = True
        load_instance = True


class PostUpdateSchema(ma.SQLAlchemyAutoSchema, PostSchemaMixin):
    class Meta:
        model = Post
        ordered = True
        fields = ("post_heading", "post_text", "post_modified_at")
        include_relationships = True
        load_instance = False
