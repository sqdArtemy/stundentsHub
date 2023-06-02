from marshmallow import fields, validate, validates, ValidationError
from models import User, Comment, Post
from app import ma
from checkers import instance_exists_by_id
from text_templates import OBJECT_DOES_NOT_EXIST


class CommentSchemaMixin:
    comment_text = fields.Str(required=False, validate=validate.Length(min=1, max=250))
    comment_created_at = fields.DateTime(required=False)
    comment_modified_at = fields.DateTime(required=False)
    comment_author = fields.Integer(required=False)
    comment_post = fields.Integer(required=False)

    @validates("comment_author")
    def validate_comment_author(self, value):
        if not instance_exists_by_id(_id=value, model=User):
            raise ValidationError(OBJECT_DOES_NOT_EXIST.format("User", value))

    @validates("comment_post")
    def validate_comment_post(self, value):
        if not instance_exists_by_id(_id=value, model=Post):
            raise ValidationError(OBJECT_DOES_NOT_EXIST.format("Post", value))


class CommentGetSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Comment
        ordered = True
        fields = ("comment_id", "comment_text", "comment_created_at",
                  "comment_modified_at", "comment_author", "comment_post")
        include_relationships = True
        load_instance = True


class CommentCreateSchema(ma.SQLAlchemyAutoSchema, CommentSchemaMixin):
    comment_text = fields.Str(required=True, validate=validate.Length(min=1, max=250))
    comment_created_at = fields.DateTime(required=True)
    comment_modified_at = fields.DateTime(required=False)
    comment_author = fields.Integer(required=False)
    comment_post = fields.Integer(required=False)

    class Meta:
        model = Comment
        ordered = True
        fields = ("comment_text", "comment_created_at", "comment_modified_at", "comment_author", "comment_post")
        include_relationships = True
        load_instance = True


class CommentUpdateSchema(ma.SQLAlchemyAutoSchema, CommentSchemaMixin):
    class Meta:
        model = Comment
        ordered = True
        fields = ("comment_text", "comment_modified_at")
        include_relationships = True
        load_instance = False
