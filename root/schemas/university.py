from marshmallow import fields, validates, ValidationError
from models import University
from .faculty import FacultyGetSchema
from app import ma
from checkers import is_name_valid, is_email_valid, instance_exists_by_id, is_phone_valid


class UniversitySchemaMixin:
    university_name = fields.Str(required=False, validate=is_name_valid)
    university_email = fields.Email(required=True, validate=is_email_valid)
    university_phone = fields.Str(required=True, validate=is_phone_valid)

    @validates("university_email")
    def validate_university_email(self, value):
        if len(University.query.filter_by(university_email=value)):
            raise ValidationError("University with this email is already exists.")


class UniversityGetSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = University
        fields = ("university_id", "university_name", "university_email", "university_phone", "university_faculties")
        include_relationships = True

    university_faculties = fields.Nested(FacultyGetSchema, many=True)


class UniversityUpdateSchema(ma.SQLAlchemyAutoSchema, UniversitySchemaMixin):
    class Meta:
        model = University
        fields = ("university_name", "university_email", "university_phone")
        include_relationships = True


class UniversityCreateSchema(ma.SQLAlchemyAutoSchema, UniversitySchemaMixin):
    university_name = fields.Str(required=True, validate=is_name_valid)
    university_email = fields.Email(required=True, validate=is_email_valid)
    university_phone = fields.Str(required=True, validate=is_phone_valid)

    class Meta:
        model = University
        fields = ("university_name", "university_email", "university_phone")
        load_instance = True
        include_relationships = True
