from db_init import db
from models.mixins import ModelMixinQuerySimplifier


chatroom_user = db.Table(
    "chatroom_user",
    db.Column("chatroom_id", db.Integer, db.ForeignKey("chat_rooms.chatroom_id")),
    db.Column("user_id", db.Integer, db.ForeignKey("users.user_id"))
)


class ChatRoom(db.Model, ModelMixinQuerySimplifier):
    __tablename__ = "chat_rooms"

    chatroom_id = db.Column(db.Integer, primary_key=True)
    chatroom_members = db.relationship("User", secondary=chatroom_user, backref="user_chat_rooms")
    chatroom_messages = db.relationship(
        "Message",
        backref="chatroom",
        foreign_keys="Message.message_chatroom",
        lazy=True,
        cascade="all, delete"
    )

    def __int__(self, chatroom_members):
        self.chatroom_members = chatroom_members

    def __repr__(self):
        return self.chatroom_id
