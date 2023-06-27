from db_init import db
from models.mixins import ModelMixinQuerySimplifier


class Role(db.Model, ModelMixinQuerySimplifier):
    __tablename__ = "user_roles"

    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), nullable=False)
    role_users = db.relationship("User", backref="role", cascade="all, delete", lazy=True)

    def __init__(self, role_name: str):
        self.role_name = role_name

    def __repr__(self):
        return f"{self.role_name}"
