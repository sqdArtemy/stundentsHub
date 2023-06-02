from db_init import db


class University(db.Model):
    __tablename__ = "universities"

    university_id = db.Column(db.Integer, primary_key=True)
    university_name = db.Column(db.String(60), nullable=False)
    university_email = db.Column(db.String(100), nullable=False, unique=True)
    university_phone = db.Column(db.String(50), nullable=False)
    university_users = db.relationship("User", backref="university", cascade="all, delete", lazy=True)
    university_faculties = db.relationship("Faculty", backref="university", cascade="all, delete", lazy=True)

    def serialize(self):
        return {
            "university_id": self.universoty_id,
            "university_name": self.university_name,
            "university_email": self.university_email,
            "university_phone": self.university_phone
        }

    def create(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def save_changes():
        db.session.commit()

    def __init__(self, university_name: str, university_email: str, university_phone: str):
        self.university_name = university_name
        self.university_phone = university_phone
        self.university_email = university_email

    def __repr__(self):
        return f"uni: {self.university_name}"
