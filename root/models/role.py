from db_init import db


class Role(db.Model):
    __tablename__ = "user_roles"

    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), nullable=False)
    role_users = db.relationship("User", backref="role", cascade="all, delete", lazy=True)

    def create(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def save_changes():
        db.session.commit()

    def __init__(self, role_name: str):
        self.role_name = role_name

    def __repr__(self):
        return f"{self.role_name}"
