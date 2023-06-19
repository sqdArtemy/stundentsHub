from db_init import db
from datetime import datetime
from .mixins import ModelMixinQuerySimplifier


class Notification(db.Model, ModelMixinQuerySimplifier):
    notification_id = db.Column(db.Integer, primary_key=True)
    notification_text = db.Column(db.String(100))
    notification_receiver = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"))
    notification_is_seen = db.Column(db.Boolean, default=False)
    notification_created_at = db.Column(db.DateTime, default=datetime.utcnow().isoformat())
    notification_sender_url = db.Column(db.String(100), nullable=True)

    def __init__(self, notification_text, notification_receiver, notification_is_seen=False,
                 notification_sender_url=None):
        self.notification_text = notification_text
        self.notification_receiver = notification_receiver
        self.notification_is_seen = notification_is_seen
        self.notification_sender_url = notification_sender_url

    def __repr__(self):
        return f"Notification {self.notification_id} to {self.notification_receiver}"
