import http_codes
from sqlalchemy.orm import joinedload
from models import Notification, User
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from schemas import NotificationGetSchema
from flask_restful import Resource, reqparse, abort
from text_templates import OBJECT_DOES_NOT_EXIST, OBJECT_DELETED, OBJECT_DELETE_NOT_ALLOWED, OBJECT_EDIT_NOT_ALLOWED, \
    OBJECT_VIEW_NOT_ALLOWED
from utilities import is_authorized_error_handler
from views.mixins import PaginationMixin, FilterMixin, SortMixin
from views.technical import sort_filter_parser


class NotificationListView(Resource, PaginationMixin, FilterMixin, SortMixin):
    notifications_get_schema = NotificationGetSchema(many=True)

    @jwt_required()
    def get(self):
        data = sort_filter_parser.parse_args()
        filters = data.get("filters")
        sort_by = data.get("sort_by")

        notifications_query = Notification.query.options(
            joinedload(Notification.receiver)
        )

        if filters:
            filter_mappings = {"notification_receiver": (Notification.receiver, User.user_id)}
            notifications_query = self.get_filtered_query(
                query=notifications_query,
                model=Notification,
                filters=filters,
                filter_mappings=filter_mappings
            )

        if sort_by:
            notifications_query = self.get_sorted_query(
                query=notifications_query,
                model=Notification,
                sort_fields=sort_by,
                sort_mappings={"notification_receiver": (User, User.user_id)}
            )
        else:
            notifications_query = notifications_query.order_by(Notification.notification_id)

        response = self.get_paginated_response(
            query=notifications_query,
            items_schema=self.notifications_get_schema,
            model_plural_name="notifications",
            count_field_name="notification_count"
        )

        return response


class NotificationDetailedView(Resource):
    notification_get_schema = NotificationGetSchema()

    @is_authorized_error_handler()
    @jwt_required()
    def get(self, notification_id: int):
        notification = Notification.query.get_or_404(
            notification_id,
            description=OBJECT_DOES_NOT_EXIST.format("Notification", notification_id)
        )
        requester = User.query.get(get_jwt_identity())
        if requester is not notification.notification_receiver:
            abort(http_codes.HTTP_FORBIDDEN_403, error_message=OBJECT_VIEW_NOT_ALLOWED.format("notification"))

        return jsonify(self.notification_get_schema.dump(notification))

    @classmethod
    @is_authorized_error_handler()
    @jwt_required()
    def delete(cls, notification_id: int):
        notification = Notification.query.get_or_404(
            notification_id,
            description=OBJECT_DOES_NOT_EXIST.format("Notification", notification_id)
        )
        requester = User.query.get(get_jwt_identity())
        if requester is not notification.notification_receiver:
            abort(http_codes.HTTP_FORBIDDEN_403, error_message=OBJECT_DELETE_NOT_ALLOWED.format("notification"))

        notification.delete()

        return {"success": OBJECT_DELETED.format("Notification", notification_id)}, http_codes.HTTP_NO_CONTENT_204

    @is_authorized_error_handler()
    @jwt_required()
    def put(self, notification_id):
        notification = Notification.query.get_or_404(
            notification_id,
            description=OBJECT_DOES_NOT_EXIST.format("Notification", notification_id)
        )

        requester = User.query.get(get_jwt_identity())
        if requester is not notification.notification_receiver:
            abort(http_codes.HTTP_FORBIDDEN_403, error_message=OBJECT_EDIT_NOT_ALLOWED.format("notification"))

        parser = reqparse.RequestParser()
        parser.add_argument("is_seen", type=bool, location="form", required=True)
        data = parser.parse_args()

        if data["is_seen"] is True:
            notification.notification_is_seen = True

        notification.save_changes()

        return jsonify(self.notification_get_schema.dump(notification))
