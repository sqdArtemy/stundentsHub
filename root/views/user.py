import http_codes
from flask_restful import Resource, abort, reqparse
from marshmallow import ValidationError
from flask import jsonify, make_response, redirect
from flask_jwt_extended import create_refresh_token, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash
from models import User
from schemas import UserCreateSchema, UserGetSchema, UserUpdateSchema
from text_templates import OBJECT_DOES_NOT_EXIST, OBJECT_DELETED, OBJECT_EDIT_NOT_ALLOWED, PAGE_NOT_FOUND
from checkers import is_authorized_error_handler
from db_init import db

parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument("user_name", location="form")
parser.add_argument("user_surname", location="form")
parser.add_argument("user_email", location="form")
parser.add_argument("user_card_id", location="form")
parser.add_argument("user_birthday", location="form")
parser.add_argument("user_role", type=int, location="form")
parser.add_argument("user_faculty", type=int, location="form")
parser.add_argument("user_university", type=int, location="form")
parser.add_argument("user_enrolment_year", location="form")
parser.add_argument("user_tg_link", location="form")
parser.add_argument("user_phone", location="form")


class UserRegisterView(Resource):
    user_create_schema = UserCreateSchema()
    user_get_schema = UserGetSchema()

    def post(self):
        parser.add_argument("user_password", location="form")
        data = parser.parse_args()

        try:
            user = self.user_create_schema.load(data)
            user.create()

            return make_response(jsonify(self.user_get_schema.dump(user)), http_codes.HTTP_OK_200)
        except ValidationError as e:
            abort(http_codes.HTTP_BAD_REQUEST_400, error_message=str(e))


class UserLoginView(Resource):
    @classmethod
    def post(cls):
        login_parser = reqparse.RequestParser(bundle_errors=True)
        login_parser.add_argument("email", location="form")
        login_parser.add_argument("password", location="form")
        data = login_parser.parse_args()

        user = User.query.filter_by(user_email=data.get("email")).first()
        if user:
            is_password_correct = check_password_hash(user.user_password, data.get("password"))

            if is_password_correct:
                access_token = create_access_token(identity=user.user_id)
                refresh_token = create_refresh_token(identity=user.user_id)

                return {
                    "user": {
                        "access_token": access_token,
                        "refresh_token": refresh_token
                    }
                }, http_codes.HTTP_CREATED_201
        return {"error": "Wrong credentials, try again."}, http_codes.HTTP_BAD_REQUEST_400


class UserChangePassword(Resource):
    user_update_schema = UserUpdateSchema()

    @is_authorized_error_handler()
    @jwt_required()
    def put(self):
        user = User.query.get(get_jwt_identity())

        parser_change_pw = reqparse.RequestParser(bundle_errors=True)
        parser_change_pw.add_argument("old_password", required=True, location="form")
        parser_change_pw.add_argument("new_password", required=True, location="form")
        parser_change_pw.add_argument("new_password_repeated", required=True, location="form")
        data = parser_change_pw.parse_args()

        is_password_correct = check_password_hash(user.user_password, data["old_password"])
        if not is_password_correct:
            abort(http_codes.HTTP_BAD_REQUEST_400, error_message="Old password is incorrect, try again.")

        if data["new_password"] != data["new_password_repeated"]:
            abort(http_codes.HTTP_BAD_REQUEST_400, error_message="New password fields do not match.")

        if data["new_password"] == data["old_password"]:
            abort(http_codes.HTTP_BAD_REQUEST_400, error_message="New password can not be the same as the old one.")

        data = {"user_password": data["new_password"]}

        try:
            updated_user = self.user_update_schema.load(data)
            for key, value in updated_user.items():
                setattr(user, key, value)
            user.save_changes()

            return {"success": "Password was changed successfully."}
        except ValidationError as e:
            abort(http_codes.HTTP_BAD_REQUEST_400, error_message=str(e))


class UserMeView(Resource):
    user_schema = UserGetSchema()

    @is_authorized_error_handler()
    @jwt_required()
    def get(self):
        return redirect(f"/user/{get_jwt_identity()}")


class UserFollowView(Resource):
    user_get_schema = UserGetSchema()

    @staticmethod
    def follow_user(follower: User, user_to_follow: User):
        if user_to_follow in follower.user_following or follower in user_to_follow.user_followers:
            abort(http_codes.HTTP_BAD_REQUEST_400, error_message="You are already following this user!")

        follower.user_following.append(user_to_follow)
        follower.save_changes()

        return user_to_follow

    @staticmethod
    def unfollow_user(unfollower: User, user_to_unfollow: User):
        if user_to_unfollow not in unfollower.user_following or unfollower not in user_to_unfollow.user_followers:
            abort(http_codes.HTTP_BAD_REQUEST_400, error_message="You are not following this user!")

        unfollower.user_following.remove(user_to_unfollow)
        unfollower.save_changes()

        return user_to_unfollow

    @is_authorized_error_handler()
    @jwt_required()
    def put(self, user_id: int):
        follow_parser = reqparse.RequestParser()
        follow_parser.add_argument("action", required=True, choices=["follow", "unfollow"], location="form")
        data = follow_parser.parse_args()

        user_to_follow = User.query.get(user_id)
        follower = User.query.get(get_jwt_identity())

        if not user_to_follow:
            abort(http_codes.HTTP_BAD_REQUEST_400, error_message=OBJECT_DOES_NOT_EXIST.format("User", user_id))

        if user_to_follow is follower:
            abort(http_codes.HTTP_BAD_REQUEST_400, error_message="You can not follow yourself.")

        if data["action"] == "follow":
            user_to_follow = self.follow_user(follower, user_to_follow)
        elif data["action"] == "unfollow":
            user_to_follow = self.unfollow_user(follower, user_to_follow)
        else:
            abort(http_codes.HTTP_BAD_REQUEST_400, error_message="Incorrect action.")

        return jsonify(self.user_get_schema.dump(user_to_follow))


class UserListViewSet(Resource):
    users_schema = UserGetSchema(many=True)

    @is_authorized_error_handler()
    @jwt_required()
    def get(self):
        users = User.query.all()
        return jsonify(self.users_schema.dump(users))


class UserDetailedViewSet(Resource):
    user_get_schema = UserGetSchema()
    user_update_schema = UserUpdateSchema()

    @is_authorized_error_handler()
    @jwt_required()
    def get(self, user_id: int):
        user = User.query.get(user_id)
        if not user:
            abort(http_codes.HTTP_NOT_FOUND_404, error_message=OBJECT_DOES_NOT_EXIST.format("User", user_id))

        return jsonify(self.user_get_schema.dump(user))

    @classmethod
    @is_authorized_error_handler()
    @jwt_required()
    def delete(cls, user_id: int):
        user = User.query.get(user_id)
        if not user:
            abort(http_codes.HTTP_NOT_FOUND_404, error_message=OBJECT_DOES_NOT_EXIST.format("User", user_id))
        user.delete()

        return {"success": OBJECT_DELETED.format("User", user_id)}, http_codes.HTTP_NO_CONTENT_204

    @is_authorized_error_handler()
    @jwt_required()
    def put(self, user_id: int):
        user = User.query.get(user_id)
        if not user:
            abort(http_codes.HTTP_NOT_FOUND_404, error_message=OBJECT_DOES_NOT_EXIST.format("User", user_id))

        requester = User.query.get(get_jwt_identity())
        if requester is not user:
            abort(http_codes.HTTP_FORBIDDEN_403, error_message=OBJECT_EDIT_NOT_ALLOWED.format("User"))

        data = parser.parse_args()
        data = {key: value for key, value in data.items() if value}

        try:
            updated_user = self.user_update_schema.load(data)
            for key, value in updated_user.items():
                setattr(user, key, value)
            user.save_changes()

            return jsonify(self.user_get_schema.dump(user))
        except ValidationError as e:
            abort(http_codes.HTTP_BAD_REQUEST_400, error_message=str(e))
