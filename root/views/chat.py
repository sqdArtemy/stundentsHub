from datetime import datetime
from sqlalchemy import or_, text
from db_init import db
from sqlalchemy.orm import joinedload
from flask import render_template
from app_init import socketio, app
from flask_socketio import join_room, leave_room, emit
from models import User, ChatRoom, Message
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from utilities import is_authorized_error_handler
from text_templates import OBJECT_DOES_NOT_EXIST


class ChatView(Resource):

    @is_authorized_error_handler()
    @jwt_required()
    def get(self, receiver_id: int):
        with db.session.begin():
            receiver = User.query.get_or_404(receiver_id, description=OBJECT_DOES_NOT_EXIST.format("User", receiver_id))
            sender = User.query.get(get_jwt_identity())

            if sender is receiver:
                room = db.session.execute(
                    text("""
                        SELECT cr.chatroom_id
                        FROM chat_rooms cr
                        JOIN chatroom_user cru ON cr.chatroom_id = cru.chatroom_id
                        GROUP BY cr.chatroom_id
                        HAVING COUNT(cru.user_id) = 1
                        LIMIT 1
                        """),
                    {"room_member_id": receiver_id}
                ).fetchone()

                if not room:
                    room = ChatRoom(chatroom_members=[sender])
                    room.create()

            else:
                room = ChatRoom.query.filter(
                    ChatRoom.chatroom_members.any(User.user_id == sender.user_id),
                    ChatRoom.chatroom_members.any(User.user_id == receiver_id)
                ).first()

                if not room:
                    room = ChatRoom(chatroom_members=[receiver, sender])
                    room.create()

            messages = Message.query.options(joinedload(Message.sender), joinedload(Message.receiver)).filter(
                or_(
                    (Message.message_sender == sender.user_id) & (Message.message_receiver == receiver_id),
                    (Message.message_sender == receiver_id) & (Message.message_receiver == sender.user_id)
                )
            ).order_by(Message.message_created_at).all()

            for message in messages:
                if message.receiver.user_id == sender.user_id and not message.message_is_read:
                    message.message_is_read = True

            response = app.make_response(
                render_template(
                    "room.html",
                    room_id=room.chatroom_id,
                    sender_id=sender.user_id,
                    receiver_id=receiver_id,
                    messages=messages,
                )
            )
            response.headers['Content-Type'] = 'text/html'

        return response


@socketio.on("join_room")
def join(data):
    if not data.get("room_id"):
        return
    join_room(int(data.get("room_id")))


@socketio.on("leave_room")
def leave(data):
    if not data.get("room_id"):
        return
    leave_room(int(data.get("room_id")))


@socketio.on("message")
def message(data):
    new_message = Message(
        message_text=data.get("text"),
        sender=User.query.get(data.get("sender_id")),
        receiver=User.query.get(data.get("receiver_id")),
        message_chatroom=data.get("room_id"),
        message_created_at=datetime.utcnow().isoformat()
    )
    new_message.create()

    emit("display_message",
         {
             "name": new_message.sender.user_name,
             "surname": new_message.sender.user_surname,
             "text": new_message.message_text,
             "date": str(new_message.message_created_at),
             "img_url": new_message.sender.user_image.file_url if new_message.sender.user_image else None,
             "is_read": new_message.message_is_read
         },
         room=int(data.get("room_id"))
         )

@socketio.on("message_read")
def message_read(data):
    print(data)
    message_id = data.get("message_id")

    # Update the is_read status of the message in the database
    message = Message.query.get(message_id)
    if message:
        message.message_is_read = True
        db.session.commit()

        # Emit an event to the sender's room to notify them about the read status
        emit("message_read_status", {"message_id": message_id}, room=message.sender.user_id)