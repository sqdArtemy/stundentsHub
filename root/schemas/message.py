from app_init import ma
from db_init import db
from models import Message, User
from marshmallow import fields, validates, validate, ValidationError, EXCLUDE
from utilities import instance_exists_by_id
from text_templates import OBJECT_DOES_NOT_EXIST
from .user import UserGetSchema


class MessageSchemaMixin:
    message_text = fields.Str(required=True, validate=validate.Length(min=1, max=1000))

    @classmethod
    def validate_message_user(cls, value):
        if not instance_exists_by_id(model=User, _id=value):
            raise ValidationError(OBJECT_DOES_NOT_EXIST.format("User", value))

    @validates("message_sender")
    def validate_message_sender(self, value):
        self.validate_message_user(value)

    @validates("message_receiver")
    def validate_message_receiver(self, value):
        self.validate_message_user(value)


class MessageGetSchema(ma.SQLAlchemyAutoSchema):
    sender = fields.Nested(UserGetSchema(only=("user_id", "user_name", "user_surname", "user_image")),
                           data_key="message_sender")
    receiver = fields.Nested(UserGetSchema(only=("user_id", "user_name", "user_surname", "user_image")),
                             data_key="message_receiver")

    class Meta:
        model = Message
        fields = ("message_id", "message_text", "message_is_read", "message_created_at", "message_updated_at",
                  "sender", "receiver")
        ordered = True
        include_relationships = True
        load_instance = True
        include_fk = True
        sqla_session = db.session


class MessageCreateSchema(ma.SQLAlchemyAutoSchema, MessageSchemaMixin):
    sender = fields.Nested(UserGetSchema(only=["user_id"]), data_key="message_sender")
    receiver = fields.Nested(UserGetSchema(only=["user_id"]), data_key="message_receiver")

    class Meta:
        model = Message
        fields = ("message_text", "sender", "receiver")
        include_relationships = True
        load_instance = True
        include_fk = True
        sqla_session = db.session
        unknown = EXCLUDE


class MessageUpdateSchema(ma.SQLAlchemyAutoSchema, MessageSchemaMixin):
    class Meta:
        model = Message
        fields = ("message_text", "message_updated_at")
        include_relationships = True
        load_instance = False
        include_fk = True
        sqla_session = db.session
        unknown = EXCLUDE
