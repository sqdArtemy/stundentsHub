from flask_restful import Resource, abort
from marshmallow import ValidationError
from flask import jsonify, make_response
from models import University
from schemas import UniversityGetSchema, UniversityCreateSchema,UniversityUpdateSchema
from app import parser
from text_templates import OBJECT_DOES_NOT_EXIST, OBJECT_DELETED
from checkers import instance_exists


class UniversityListView(Resource):
    universities_get_schema = UniversityGetSchema(many=True)
    university_get_schema = UniversityGetSchema()
    university_create_schema = UniversityCreateSchema()

    def get(self):
        universities = University.query.all()
        return jsonify(self.universities_get_schema.dump(universities))

    def post(self):
        parser.add_argument("university_name", location="form")
        parser.add_argument("university_email", location="form")
        parser.add_argument("university_phone", location="form")
        data = parser.parse_args()

        try:
            university = self.university_create_schema.load(data)
            university.create()

            return make_response(jsonify(self.university_get_schema.dump(university)), 201)
        except ValidationError as e:
            abort(400, error_message=str(e))


class UniversityDetailedView(Resource):
    university_get_schema = UniversityGetSchema()
    university_update_schema = UniversityUpdateSchema()

    def get(self, university_id: int):
        university = University.query.get(university_id)
        if not instance_exists(university):
            abort(404, error_message=OBJECT_DOES_NOT_EXIST.format("University", university_id))

        return jsonify(self.university_get_schema.dump(university))

    @classmethod
    def delete(cls, university_id: int):
        university = University.query.get(university_id)
        if not instance_exists(university):
            abort(404, error_message=OBJECT_DOES_NOT_EXIST.format("University", university_id))
        university.delete()

        return {"success": OBJECT_DELETED.format("University", university_id)}, 200

    def put(self, university_id: int):
        university = University.query.get(university_id)
        if not instance_exists(university):
            abort(404, error_message=OBJECT_DOES_NOT_EXIST.format("University", university_id))

        parser.add_argument("university_name", required=False, location="form")
        parser.add_argument("university_email", required=False, location="form")
        parser.add_argument("university_phone", required=False, location="form")
        data = parser.parse_args()
        data = {key: value for key, value in data.items() if value}

        try:
            updated_university = self.university_update_schema.load(data)
            for key, value in updated_university:
                setattr(university, key, value)
            university.save_changes()

            return jsonify(self.university_get_schema.dump(university))
        except ValidationError as e:
            abort(400, error_message=str(e))





