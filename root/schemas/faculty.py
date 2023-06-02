from marshmallow import fields, validates, ValidationError
from models import Faculty, University
from app import ma
from checkers import is_name_valid, instance_exists_by_id


class FacultySchemaMixin:
    faculty_name = fields.Str(required=False, validate=is_name_valid)
    faculty_university = fields.Integer(required=False)

    @validates("faculty_university")
    def validate_faculty_university(self, value):
        if not instance_exists_by_id(_id=value, model=University):
            raise ValidationError(f"University with id = {value} does not exist.")


class FacultyGetSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Faculty
        fields = ("faculty_id", "faculty_name", "faculty_university")
        ordered = True


class FacultyUpdateSchema(ma.SQLAlchemyAutoSchema, FacultySchemaMixin):
    class Meta:
        model = Faculty
        fields = ("faculty_name", "faculty_university")
        include_relationships = True


class FacultyCreateSchema(ma.SQLAlchemyAutoSchema, FacultySchemaMixin):
    faculty_name = fields.Str(required=True, validate=is_name_valid)
    faculty_university = fields.Integer(required=True)

    class Meta:
        model = Faculty
        fields = ("faculty_name", "faculty_university")
        load_instance = True
        include_relationships = True
