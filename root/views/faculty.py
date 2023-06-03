from flask_restful import Resource, abort
from marshmallow import ValidationError
from flask import jsonify, make_response
from flask_jwt_extended import jwt_required
from models import Faculty
from schemas import FacultyGetSchema, FacultyCreateSchema, FacultyUpdateSchema
from app_init import parser
from text_templates import OBJECT_DOES_NOT_EXIST, OBJECT_DELETED
from checkers import instance_exists, is_authorized_error_handler


class FacultyListView(Resource):
    faculties_get_schema = FacultyGetSchema(many=True)
    faculty_get_schema = FacultyGetSchema()
    faculty_create_schema = FacultyCreateSchema()

    @is_authorized_error_handler()
    @jwt_required()
    def get(self):
        faculties = Faculty.query.all()
        return jsonify(self.faculties_get_schema.dump(faculties))

    @is_authorized_error_handler()
    @jwt_required()
    def post(self):
        parser.add("faculty_name", location="form")
        parser.add("faculty_university", location="form")
        data = parser.parse_args()

        try:
            faculty = self.faculty_create_schema.load(data)
            faculty.create()

            return make_response(jsonify(self.faculty_get_schema.dump(faculty)), 201)
        except ValidationError as e:
            abort(400, error_mesage=e)


class FacultyDetailedView(Resource):
    faculty_get_schema = FacultyGetSchema()
    faculty_update_schema = FacultyUpdateSchema()

    @is_authorized_error_handler()
    @jwt_required()
    def get(self, faculty_id: int):
        faculty = Faculty.query.get(faculty_id)
        if not instance_exists(faculty):
            abort(404, error_message=OBJECT_DOES_NOT_EXIST.format("Faculty", faculty_id))

        return jsonify(self.faculty_get_schema.dump(faculty))

    @classmethod
    @is_authorized_error_handler()
    @jwt_required()
    def delete(cls, faculty_id: int):
        faculty = Faculty.query.get(faculty_id)
        if not instance_exists(faculty):
            abort(404, error_message=OBJECT_DOES_NOT_EXIST.format("Faculty", faculty_id))
        faculty.delete()

        return {"success": OBJECT_DELETED.format("Faculty", faculty_id)}, 200

    @is_authorized_error_handler()
    @jwt_required()
    def put(self, faculty_id: int):
        faculty = Faculty.query.get(faculty_id)
        if not instance_exists(faculty):
            abort(404, error_message=OBJECT_DOES_NOT_EXIST.format("Faculty", faculty_id))

        parser.add("faculty_name", location="form")
        parser.add("faculty_university", location="form")
        data = parser.parse_args()
        data = {key: value for key, value in data.items() if value}

        try:
            updated_faculty = self.faculty_update_schema.load(data)
            for key, value in updated_faculty:
                setattr(faculty, key, value)
            faculty.save_changes()

            return jsonify(self.faculty_get_schema.dump(faculty))
        except ValidationError as e:
            abort(400, error_message=str(e))
