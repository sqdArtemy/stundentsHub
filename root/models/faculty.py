from db_init import db
from .mixins import ModelMixinQuerySimplifier


class Faculty(db.Model, ModelMixinQuerySimplifier):
    __tablename__ = "faculties"

    faculty_id = db.Column(db.Integer, primary_key=True)
    faculty_name = db.Column(db.String(100), nullable=False)
    faculty_university = db.Column(
        db.Integer, db.ForeignKey("universities.university_id", ondelete="CASCADE"), nullable=False
    )
    faculty_users = db.relationship("User", backref="faculty", cascade="all, delete", lazy=True)

    def __init__(self, faculty_name: str, faculty_university: int):
        self.faculty_name = faculty_name
        self.faculty_university = faculty_university

    def __repr__(self):
        return f"{self.faculty_name}"
