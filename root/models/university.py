from db_init import db
from .mixins import ModelMixinQuerySimplifier


class University(db.Model, ModelMixinQuerySimplifier):
    __tablename__ = "universities"

    university_id = db.Column(db.Integer, primary_key=True)
    university_name = db.Column(db.String(60), nullable=False)
    university_email = db.Column(db.String(100), nullable=False, unique=True)
    university_phone = db.Column(db.String(50), nullable=False)
    university_users = db.relationship("User", backref="university", cascade="all, delete", lazy=True)
    university_faculties = db.relationship("Faculty", backref="university", cascade="all, delete", lazy=True)
    university_image_id = db.Column(db.Integer, db.ForeignKey("files.file_id", ondelete="CASCADE"), nullable=True)
    university_image = db.relationship("File", backref="uploaded_by_uni", cascade="all, delete", lazy=True)

    def __init__(self, university_name: str, university_email: str, university_phone: str, university_image=None):
        self.university_name = university_name
        self.university_phone = university_phone
        self.university_email = university_email
        if university_image:
            self.university_image = university_image
            self.university_image_if = university_image.file_id

    def __repr__(self):
        return f"uni: {self.university_name}"
