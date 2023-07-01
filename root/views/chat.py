from sqlalchemy import or_
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

    # @is_authorized_error_handler()
    # @jwt_required()
    def get(self, receiver_id: int):
        receiver = User.query.get_or_404(receiver_id, description=OBJECT_DOES_NOT_EXIST.format("User", receiver_id))
        sender = User.query.get(21)
        # sender_id = get_jwt_identity()

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
        ).all()

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
    join_room(data.get("room_id"))


@socketio.on("leave_room")
def leave(data):
    leave_room(data.get("room_id"))


@socketio.on("message")
def message(data):
    new_message = Message(
        message_text=data.get("text"),
        sender=User.query.get(data.get("sender_id")),
        receiver=User.query.get(data.get("receiver_id")),
        message_chatroom=data.get("room_id")
    )
    new_message.create()

    emit("display_message",
         {
             "name": new_message.sender.user_name,
             "surname": new_message.sender.user_surname,
             "text": new_message.message_text,
             "date": str(new_message.message_created_at)
         }
         )
