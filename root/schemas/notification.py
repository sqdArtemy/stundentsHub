from models import Notification
from .user import UserGetSchema
from app_init import ma
from marshmallow import fields
from db_init import db


class NotificationGetSchema(ma.SQLAlchemyAutoSchema):
    receiver = fields.Nested(
        UserGetSchema(only=("user_id", "user_name", "user_surname", "user_image")),
        data_key="notification_receiver"
    )

    class Meta:
        model = Notification
        ordered = True
        fields = ("notification_id", "notification_text", "receiver", "notification_created_at",
                  "notification_is_seen", "notification_sender_url")
        load_instance = True
        include_relationships = True
        include_fk = True
        sqla_session = db.session
