from marshmallow import fields, EXCLUDE
from models import Role
from app_init import ma
from utilities import is_name_valid


class RoleGetSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Role
        fields = ("role_id", "role_name")
        ordered = True
        unknown = EXCLUDE


class RoleCreateSchema(ma.SQLAlchemyAutoSchema):
    role_name = fields.Str(required=True, validate=is_name_valid)

    class Meta:
        model = Role
        fields = ["role_name"]
        ordered = True
        load_instance = True
        unknown = EXCLUDE


class RoleUpdateSchema(RoleGetSchema):
    role_name = fields.Str(required=False, validate=is_name_valid)
