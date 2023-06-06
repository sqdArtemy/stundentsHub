import http_codes
from flask_restful import Resource, abort, reqparse
from marshmallow import ValidationError
from flask import jsonify, make_response
from flask_jwt_extended import jwt_required
from models import Role
from schemas import RoleGetSchema, RoleCreateSchema, RoleUpdateSchema
from text_templates import MSG_MISSING, OBJECT_DOES_NOT_EXIST, OBJECT_DELETED
from checkers import is_authorized_error_handler

parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument("role_name", location="form", help=MSG_MISSING.format("role_name"))


class RoleListViewSet(Resource):
    roles_get_schema = RoleGetSchema(many=True)
    role_get_schema = RoleGetSchema()
    role_create_schema = RoleCreateSchema()

    @is_authorized_error_handler()
    @jwt_required()
    def get(self):
        roles = Role.query.all()
        return jsonify(self.roles_get_schema.dump(roles))

    @is_authorized_error_handler()
    @jwt_required()
    def post(self):
        data = parser.parse_args()

        try:
            role = self.role_create_schema.load(data)
            role.create()

            return make_response(jsonify(self.role_get_schema.dump(role)), http_codes.HTTP_CREATED_201)
        except ValidationError as e:
            abort(http_codes.HTTP_BAD_REQUEST_400, error_message=str(e))


class RoleDetailedViewSet(Resource):
    role_get_schema = RoleGetSchema()
    role_update_schema = RoleUpdateSchema()

    @is_authorized_error_handler()
    @jwt_required()
    def get(self, role_id: int):
        role = Role.query.get(role_id)
        if not role:
            abort(http_codes.HTTP_NOT_FOUND_404, error_message=OBJECT_DOES_NOT_EXIST.format("Role", role_id))
        return jsonify(self.role_get_schema.dump(role))

    @classmethod
    @is_authorized_error_handler()
    @jwt_required()
    def delete(cls, role_id: int):
        role = Role.query.get(role_id)
        if not role:
            abort(http_codes.HTTP_NOT_FOUND_404, error_message=OBJECT_DOES_NOT_EXIST.format("Role", role_id))
        role.delete()

        return {"success": OBJECT_DELETED.format("Role", role_id)}, http_codes.HTTP_NO_CONTENT_204

    @is_authorized_error_handler()
    @jwt_required()
    def put(self, role_id: int):
        role = Role.query.get(role_id)
        if not role:
            abort(http_codes.HTTP_NOT_FOUND_404, error_message=OBJECT_DOES_NOT_EXIST.format("Role", role_id))

        data = parser.parse_args()
        data = {key: value for key, value in data.items() if value}

        try:
            updated_role = self.role_update_schema.load(data)
            for key, value in updated_role.items():
                setattr(role, key, value)
            role.save_changes()

            return jsonify(self.role_get_schema.dump(role))
        except ValidationError as e:
            abort(http_codes.HTTP_BAD_REQUEST_400, error_message=str(e))
