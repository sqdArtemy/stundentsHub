from db_init import db
from datetime import datetime
from sqlalchemy.event import listens_for
from models.user import User
from models.mixins import ModelMixinQuerySimplifier
from tasks import send_mail


class Notification(db.Model, ModelMixinQuerySimplifier):
    __tablename__ = "notifications"

    notification_id = db.Column(db.Integer, primary_key=True)
    notification_text = db.Column(db.String(100))
    notification_receiver = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"))
    notification_is_seen = db.Column(db.Boolean, default=False)
    notification_created_at = db.Column(db.DateTime, default=datetime.utcnow().isoformat())
    notification_sender_url = db.Column(db.String(100), nullable=True)

    def __init__(self, notification_text, notification_receiver, notification_is_seen=False,
                 notification_sender_url=None):
        self.notification_text = notification_text
        self.notification_receiver = notification_receiver.user_id
        self.notification_is_seen = notification_is_seen
        self.notification_sender_url = notification_sender_url

    def __repr__(self):
        return f"Notification {self.notification_id} to {self.notification_receiver}"


@listens_for(Notification, "after_insert")
def send_notification_by_email(mapper, connection, target):
    send_mail.delay(
        subject="New notification has been received!",
        recipients=[User.query.get(target.notification_receiver).user_email],
        body=target.notification_text
    )
