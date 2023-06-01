from marshmallow import fields
from models import Role
from app import ma
from checkers import (
    is_email_valid, instance_exists_by_id, is_phone_valid, is_name_valid, is_date_valid
)


class RoleGetSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Role
        fields = ("role_id", "role_name")
        ordered = True


class RoleCreateSchema(ma.SQLAlchemyAutoSchema):
    role_name = fields.Str(required=True, validate=is_name_valid)

    class Meta:
        model = Role
        fields = ["role_name"]
        ordered = True
        load_instance = True


class RoleUpdateSchema(RoleGetSchema):
    role_name = fields.Str(required=False, validate=is_name_valid)
