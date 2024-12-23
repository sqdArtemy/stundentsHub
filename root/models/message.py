from datetime import datetime
from db_init import db
from models.mixins import ModelMixinQuerySimplifier


class Message(db.Model, ModelMixinQuerySimplifier):
    __tablename__ = "messages"

    message_id = db.Column(db.Integer, primary_key=True)
    message_text = db.Column(db.String(1000))
    message_is_read = db.Column(db.Boolean, default=False)
    message_created_at = db.Column(db.DateTime, default=datetime.utcnow().isoformat())
    message_edited_at = db.Column(db.DateTime, nullable=True, default=None)
    message_sender = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    message_receiver = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    message_chatroom = db.Column(db.Integer, db.ForeignKey("chat_rooms.chatroom_id"))

    def __init__(self, message_text, sender, receiver, message_chatroom,
                 message_created_at, message_is_read=False, message_edited_at=None):
        self.message_text = message_text
        self.message_receiver = receiver.user_id
        self.message_sender = sender.user_id
        self.message_is_read = message_is_read
        self.message_chatroom = message_chatroom
        self.message_created_at = message_created_at

        if message_edited_at:
            self.message_edited_at = message_edited_at

    def __repr__(self):
        return f"Message: {self.message_id} from {self.message_sender} to {self.message_receiver}"

