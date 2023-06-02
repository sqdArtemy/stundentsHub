from flask_restful import Resource, abort
from marshmallow import ValidationError
from flask import jsonify, make_response
from models import Role
from schemas import RoleGetSchema, RoleCreateSchema, RoleUpdateSchema
from app import parser
from text_templates import MSG_MISSING, OBJECT_DOES_NOT_EXIST, OBJECT_DELETED
from checkers import instance_exists


class RoleListViewSet(Resource):
    roles_get_schema = RoleGetSchema(many=True)
    role_get_schema = RoleGetSchema()
    role_create_schema = RoleCreateSchema()

    def get(self):
        roles = Role.query.all()
        return jsonify(self.roles_get_schema.dump(roles))

    def post(self):
        parser.add_argument("role_name", required=True, location="form", help=MSG_MISSING.format("role_name"))
        data = parser.parse_args()

        try:
            role = self.role_create_schema.load(data)
            role.create()

            return make_response(jsonify(self.role_get_schema.dump(role)), 201)
        except ValidationError as e:
            abort(400, error_message=str(e))


class RoleDetailedViewSet(Resource):
    role_get_schema = RoleGetSchema()
    role_update_schema = RoleUpdateSchema()

    def get(self, role_id: int):
        role = Role.query.get(role_id)
        if not instance_exists(role):
            abort(404, error_message=OBJECT_DOES_NOT_EXIST.format("Role", role_id))
        return jsonify(self.role_get_schema.dump(role))

    @classmethod
    def delete(cls, role_id: int):
        role = Role.query.get(role_id)
        if not instance_exists(role):
            abort(404, error_message=OBJECT_DOES_NOT_EXIST.format("Role", role_id))
        role.delete()

        return {"success": OBJECT_DELETED.format("Role", role_id)}, 200

    def put(self, role_id: int):
        role = Role.query.get(role_id)
        if not instance_exists(role):
            abort(404, error_message=OBJECT_DOES_NOT_EXIST.format("Role", role_id))

        parser.add_argument("role_name", location="form")
        data = parser.parse_args()
        data = {key: value for key, value in data.items() if value}

        try:
            updated_role = self.role_update_schema.load(data)
            for key, value in updated_role.items():
                setattr(role, key, value)
            role.save_changes()

            return jsonify(self.role_get_schema.dump(role))
        except ValidationError as e:
            abort(400, error_message=str(e))
