from flask import make_response, jsonify, request
from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from flask_socketio import emit, join_room, leave_room, Namespace
import http_codes
from datetime import datetime
from marshmallow import ValidationError
from flask_restful import Resource, abort, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Message, User
from app_init import socketio
from schemas import MessageGetSchema, MessageUpdateSchema, MessageCreateSchema, UserGetSchema
from utilities import is_authorized_error_handler
from text_templates import OBJECT_DOES_NOT_EXIST, OBJECT_DELETE_NOT_ALLOWED, OBJECT_DELETED
from views.mixins import SortMixin, PaginationMixin, FilterMixin
from views.technical import sort_filter_parser

parser = reqparse.RequestParser()
parser.add_argument("message_text", required=True, location="form")


class MessageListView(Resource, PaginationMixin, SortMixin, FilterMixin):
    message_get_schema = MessageGetSchema()
    messages_get_schema = MessageGetSchema(many=True)
    message_create_schema = MessageCreateSchema()

    @is_authorized_error_handler()
    @jwt_required()
    def get(self, receiver_id: int):
        sender = User.query.get(get_jwt_identity())
        receiver = User.query.get_or_404(receiver_id, description=OBJECT_DOES_NOT_EXIST.format("User", receiver_id))

        data = sort_filter_parser.parse_args()
        sort_by = data["sort_by"]
        filters = data["filters"]

        messages_query = Message.query.options(
            joinedload(Message.sender),
            joinedload(Message.receiver)
        ).filter(
            or_(
                (Message.message_sender == sender.user_id) & (Message.message_receiver == receiver.user_id),
                (Message.message_sender == receiver.user_id) & (Message.message_receiver == sender.user_id)
            )
        )

        try:
            if filters:
                filter_mappings = {
                    "message_sender": (Message.sender, User.user_id),
                    "message_receiver": (Message.receiver, User.user_id)
                }

                messages_query = self.get_filtered_query(
                    query=messages_query,
                    model=Message,
                    filters=filters,
                    filter_mappings=filter_mappings
                )

            if sort_by:
                sort_mappings = {
                    "message_sender": (User, User.user_id),
                    "message_receiver": (User, User.user_id)
                }

                messages_query = self.get_sorted_query(
                    query=messages_query,
                    model=Message,
                    sort_fields=sort_by,
                    sort_mappings=sort_mappings
                )
            else:
                messages_query = messages_query.order_by(Message.message_created_at)

        except AttributeError as e:
            abort(http_codes.HTTP_BAD_REQUEST_400, error_message=str(e))

        response = self.get_paginated_response(
            query=messages_query,
            items_schema=self.messages_get_schema,
            model_plural_name="messages",
            count_field_name="message_count"
        )

        return response


class MessageDetailedView(Resource):
    message_get_schema = MessageGetSchema()
    message_update_schema = MessageUpdateSchema()

    @classmethod
    @is_authorized_error_handler()
    @jwt_required()
    def delete(cls, receiver_id: int, message_id: int):
        message = Message.query.get_or_404(message_id, description=OBJECT_DOES_NOT_EXIST.format("Message", message_id))
        receiver = User.query.get_or_404(receiver_id, description=OBJECT_DOES_NOT_EXIST.format("User", receiver_id))
        sender = User.query.get(get_jwt_identity())

        if message.sender is not sender:
            abort(http_codes.HTTP_FORBIDDEN_403, error_message=OBJECT_DELETE_NOT_ALLOWED.format("Message"))

        if message.receiver is not receiver:
            abort(http_codes.HTTP_FORBIDDEN_403, error_message="This message is from another chat!")

        message.delete()

        return {"success": OBJECT_DELETED.format("Message", message_id)}, http_codes.HTTP_NO_CONTENT_204

    @is_authorized_error_handler()
    @jwt_required()
    def put(self, receiver_id: int, message_id: int):
        message = Message.query.get_or_404(message_id, description=OBJECT_DOES_NOT_EXIST.format("Message", message_id))
        receiver = User.query.get_or_404(receiver_id, description=OBJECT_DOES_NOT_EXIST.format("User", receiver_id))
        sender = User.query.get(get_jwt_identity())

        if message.sender is not sender:
            abort(http_codes.HTTP_FORBIDDEN_403, error_message=OBJECT_DELETE_NOT_ALLOWED.format("Message"))

        if message.receiver is not receiver:
            abort(http_codes.HTTP_FORBIDDEN_403, error_message="This message is from another chat!")

        data = parser.parse_args()
        data["message_updated_at"] = datetime.utcnow().isoformat()
        data = {key: value for key, value in data.items() if value}

        try:
            updated_message = self.message_update_schema.load(data)
            for key, value in updated_message.items():
                setattr(message, key, value)

            message.save_changes()

            return jsonify(self.message_get_schema.dump(message))
        except ValidationError as e:
            abort(http_codes.HTTP_BAD_REQUEST_400, error_message=str(e))
