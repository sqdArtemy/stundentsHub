import http_codes
from flask_restful import Resource, abort, reqparse
from marshmallow import ValidationError
from flask import jsonify, make_response
from flask_jwt_extended import jwt_required
from models import University
from schemas import UniversityGetSchema, UniversityCreateSchema, UniversityUpdateSchema
from text_templates import OBJECT_DOES_NOT_EXIST, OBJECT_DELETED
from checkers import is_authorized_error_handler

parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument("university_name", location="form")
parser.add_argument("university_email", location="form")
parser.add_argument("university_phone", location="form")


class UniversityListView(Resource):
    universities_get_schema = UniversityGetSchema(many=True)
    university_get_schema = UniversityGetSchema()
    university_create_schema = UniversityCreateSchema()

    @is_authorized_error_handler()
    @jwt_required()
    def get(self):
        universities = University.query.all()
        return jsonify(self.universities_get_schema.dump(universities))

    @is_authorized_error_handler()
    @jwt_required()
    def post(self):
        data = parser.parse_args()

        try:
            university = self.university_create_schema.load(data)
            university.create()

            return make_response(jsonify(self.university_get_schema.dump(university)), http_codes.HTTP_CREATED_201)
        except ValidationError as e:
            abort(http_codes.HTTP_BAD_REQUEST_400, error_message=str(e))


class UniversityDetailedView(Resource):
    university_get_schema = UniversityGetSchema()
    university_update_schema = UniversityUpdateSchema()

    @is_authorized_error_handler()
    @jwt_required()
    def get(self, university_id: int):
        university = University.query.get(university_id)
        if not university:
            abort(http_codes.HTTP_NOT_FOUND_404,
                  error_message=OBJECT_DOES_NOT_EXIST.format("University", university_id))

        return jsonify(self.university_get_schema.dump(university))

    @classmethod
    @is_authorized_error_handler()
    @jwt_required()
    def delete(cls, university_id: int):
        university = University.query.get(university_id)
        if not university:
            abort(http_codes.HTTP_NOT_FOUND_404,
                  error_message=OBJECT_DOES_NOT_EXIST.format("University", university_id))
        university.delete()

        return {"success": OBJECT_DELETED.format("University", university_id)}, 200

    @is_authorized_error_handler()
    @jwt_required()
    def put(self, university_id: int):
        university = University.query.get(university_id)
        if not university:
            abort(http_codes.HTTP_NOT_FOUND_404,
                  error_message=OBJECT_DOES_NOT_EXIST.format("University", university_id))

        data = parser.parse_args()
        data = {key: value for key, value in data.items() if value}

        try:
            updated_university = self.university_update_schema.load(data)
            for key, value in updated_university:
                setattr(university, key, value)
            university.save_changes()

            return jsonify(self.university_get_schema.dump(university))
        except ValidationError as e:
            abort(http_codes.HTTP_BAD_REQUEST_400, error_message=str(e))
