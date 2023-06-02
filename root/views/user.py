from flask_restful import Resource, abort
from marshmallow import ValidationError
from flask import jsonify, make_response
from werkzeug.security import check_password_hash
from models import User
from schemas import UserCreateSchema, UserGetSchema, UserUpdateSchema
from app_init import parser
from text_templates import OBJECT_DOES_NOT_EXIST, OBJECT_DELETED
from checkers import instance_exists


class UserRegisterView(Resource):
    user_create_schema = UserCreateSchema()
    user_get_schema = UserGetSchema()

    def post(self):
        parser.add_argument("user_name", location="form")
        parser.add_argument("user_surname", location="form")
        parser.add_argument("user_email", location="form")
        parser.add_argument("user_password", location="form")
        parser.add_argument("user_card_id", location="form")
        parser.add_argument("user_birthday", location="form")
        parser.add_argument("user_role", type=int, location="form")
        parser.add_argument("user_faculty", type=int, location="form")
        parser.add_argument("user_university", type=int, location="form")
        parser.add_argument("user_enrolment_year", location="form")
        parser.add_argument("user_tg_link", location="form")
        parser.add_argument("user_phone", location="form")
        data = parser.parse_args()

        try:
            user = self.user_create_schema.load(data)
            user.create()

            return make_response(jsonify(self.user_get_schema.dump(user)), 201)
        except ValidationError as e:
            abort(400, error_message=str(e))


class UserListViewSet(Resource):
    users_schema = UserGetSchema(many=True)

    def get(self):
        users = User.query.all()
        return jsonify(self.users_schema.dump(users))


class UserDetailedViewSet(Resource):
    user_get_schema = UserGetSchema()
    user_update_schema = UserUpdateSchema()

    def get(self, user_id: int):
        user = User.query.get(user_id)
        if not instance_exists(user):
            abort(404, error_message=OBJECT_DOES_NOT_EXIST.format("User", user_id))

        return jsonify(self.user_get_schema.dump(user))

    @classmethod
    def delete(cls, user_id: int):
        user = User.query.get(user_id)
        if not instance_exists(user):
            abort(404, error_message=OBJECT_DOES_NOT_EXIST.format("User", user_id))
        user.delete()

        return {"success": OBJECT_DELETED.format("User", user_id)}, 200

    def put(self, user_id: int):
        user = User.query.get(user_id)
        if not instance_exists(user):
            abort(404, error_message=OBJECT_DOES_NOT_EXIST.format("User", user_id))

        parser.add_argument("user_name", required=False, location="form")
        parser.add_argument("user_surname", required=False, location="form")
        parser.add_argument("user_email", required=False, location="form")
        parser.add_argument("user_password", required=False, location="form")
        parser.add_argument("user_card_id", required=False, location="form")
        parser.add_argument("user_birthday", required=False, location="form")
        parser.add_argument("user_role", required=False, type=int, location="form")
        parser.add_argument("user_faculty", required=False, type=int, location="form")
        parser.add_argument("user_university", required=False, type=int, location="form",)
        parser.add_argument("user_enrolment_year", required=False, location="form",)
        parser.add_argument("user_tg_link", required=False, location="form")
        parser.add_argument("user_phone", required=False, location="form")
        data = parser.parse_args()
        data = {key: value for key, value in data.items() if value}

        try:
            updated_user = self.user_update_schema.load(data)
            for key, value in updated_user.items():
                setattr(user, key, value)
            user.save_changes()

            return jsonify(self.user_get_schema.dump(user))
        except ValidationError as e:
            abort(400, error_message=str(e))
