from db_init import db
from datetime import datetime


class Post(db.Model):
    __tablename__ = "posts"

    post_id = db.Column(db.Integer, primary_key=True)
    post_heading = db.Column(db.String(100), nullable=False)
    post_text = db.Column(db.String(2500), nullable=False)
    post_created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    post_modified_at = db.Column(db.DateTime, nullable=True, default=None)
    post_author = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    post_comments = db.relationship("Comment", backref="post", cascade="all, delete", lazy=True)

    def serialize(self):
        return {
            "post_id": self.post_id,
            "post_heading": self.post_heading,
            "post_text": self.post_text,
            "post_created_at": self.post_created_at,
            "post_modified_at": self.post_modified_at,
            "post_author": self.post_author.user_id
        }

    def __init__(self, post_heading: str, post_text: str, post_created_at: str, post_modified_at: str):
        self.post_heading = post_heading
        self.post_text = post_text
        self.post_created_at = post_created_at
        self.post_modified_at = post_modified_at

    def __repr__(self):
        return f"Post({self.post_id} {self.post_heading})"
