from models import Notification
from .user import UserGetSchema
from app_init import ma
from marshmallow import fields


class NotificationGetSchema(ma.SQLAlchemyAutoSchema):
    notification_receiver = fields.Nested(UserGetSchema(only=("user_id", "user_name", "user_surname", "user_image")))

    class Meta:
        model = Notification
        ordered = True
        fields = ("notification_id", "notification_text", "notification_receiver", "notification_created_at",
                  "notification_is_seen", "notification_sender_url")
        load_instance = True
