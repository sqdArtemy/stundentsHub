import json
import http_codes
from sqlalchemy.orm import joinedload
from flask_restful import Resource, abort, reqparse
from marshmallow import ValidationError
from flask import jsonify, make_response, request
from flask_jwt_extended import jwt_required
from models import Faculty, University
from schemas import FacultyGetSchema, FacultyCreateSchema, FacultyUpdateSchema
from text_templates import OBJECT_DOES_NOT_EXIST, OBJECT_DELETED
from utilities import is_authorized_error_handler
from .mixins import PaginationMixin


parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument("faculty_name", location="form")
parser.add_argument("faculty_university", type=int, location="form")


class FacultyListView(Resource, PaginationMixin):
    faculties_get_schema = FacultyGetSchema(many=True)
    faculty_get_schema = FacultyGetSchema()
    faculty_create_schema = FacultyCreateSchema()

    @is_authorized_error_handler()
    @jwt_required()
    def get(self):
        filters = request.args.get("filters")
        sort_by = request.args.get("sort_by")
        sort_order = request.args.get("sort_order", "asc")

        faculties_query = Faculty.query.options(joinedload(Faculty.university)).order_by(Faculty.faculty_id)

        try:
            if filters:
                filters_dict = json.loads(filters)
                for key, value in filters_dict.items():
                    if key == "faculty_university":
                        faculties_query = faculties_query.filter(
                            Faculty.university.has(University.university_name.ilike(value))
                        )
                    else:
                        faculties_query = faculties_query.filter(getattr(Faculty, key) == value)

                if sort_by:
                    column = getattr(University, sort_by)

                    if sort_by == "faculty_university":
                        column = University.university_name

                    if sort_order.lower() == "desc":
                        column = column.desc()

                    faculties_query = faculties_query.order_by(column)

        except AttributeError as e:
            abort(http_codes.HTTP_BAD_REQUEST_400, error_message=str(e))

        response = self.get_paginated_response(
            query=faculties_query,
            items_schema=self.faculties_get_schema,
            model_plural_name="faculties",
            count_field_name="faculty_count"
        )

        return response

    @is_authorized_error_handler()
    @jwt_required()
    def post(self):
        data = parser.parse_args()

        try:
            faculty = self.faculty_create_schema.load(data)
            faculty.create()

            return make_response(jsonify(self.faculty_get_schema.dump(faculty)), http_codes.HTTP_CREATED_201)
        except ValidationError as e:
            abort(http_codes.HTTP_BAD_REQUEST_400, error_mesage=str(e))


class FacultyDetailedView(Resource):
    faculty_get_schema = FacultyGetSchema()
    faculty_update_schema = FacultyUpdateSchema()

    @is_authorized_error_handler()
    @jwt_required()
    def get(self, faculty_id: int):
        faculty = Faculty.query.get_or_404(faculty_id, description=OBJECT_DOES_NOT_EXIST.format("Faculty", faculty_id))

        return jsonify(self.faculty_get_schema.dump(faculty))

    @classmethod
    @is_authorized_error_handler()
    @jwt_required()
    def delete(cls, faculty_id: int):
        faculty = Faculty.query.get_or_404(faculty_id, description=OBJECT_DOES_NOT_EXIST.format("Faculty", faculty_id))
        faculty.delete()

        return {"success": OBJECT_DELETED.format("Faculty", faculty_id)}, http_codes.HTTP_NO_CONTENT_204

    @is_authorized_error_handler()
    @jwt_required()
    def put(self, faculty_id: int):
        faculty = Faculty.query.get_or_404(faculty_id, description=OBJECT_DOES_NOT_EXIST.format("Faculty", faculty_id))

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
