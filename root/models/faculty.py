from app import db


class Faculty(db.Model):
    __tablename__ = "faculties"

    faculty_id = db.Column(db.Integer, primary_key=True)
    faculty_name = db.Column(db.String(100), nullable=False)
    faculty_university = db.Column(
        db.Integer, db.ForeignKey("universities.university_id", ondelete="CASCADE"), nullable=False
    )
    faculty_users = db.relationship("User", backref="faculty", cascade="all, delete", lazy=True)

    def create(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def save_changes():
        db.session.commit()

    def __init__(self, faculty_name: str):
        self.faculty_name = faculty_name

    def __repr__(self):
        return f"{self.faculty_name}"
