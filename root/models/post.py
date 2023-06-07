from typing import List
from db_init import db
from datetime import datetime
from .user import User


user_likes_post = db.Table(
    "user_likes_post",
    db.Column("user_id", db.Integer, db.ForeignKey("users.user_id")),
    db.Column("post_id", db.Integer, db.ForeignKey("posts.post_id"))
)

user_dislikes_post = db.Table(
    "user_dislikes_post",
    db.Column("user_id", db.Integer, db.ForeignKey("users.user_id")),
    db.Column("post_id", db.Integer, db.ForeignKey("posts.post_id"))
)


class Post(db.Model):
    __tablename__ = "posts"

    post_id = db.Column(db.Integer, primary_key=True)
    post_heading = db.Column(db.String(100), nullable=False)
    post_text = db.Column(db.String(2500), nullable=False)
    post_created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    post_modified_at = db.Column(db.DateTime, nullable=True, default=None)
    post_author = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    post_comments = db.relationship("Comment", backref="post", cascade="all, delete", lazy=True)
    post_likes = db.Column(db.Integer, default=0)
    post_dislikes = db.Column(db.Integer, default=0)
    post_rating = db.Column(db.Float, default=0)
    post_liked_by = db.relationship("User", secondary=user_likes_post, backref="user_liked_posts")
    post_disliked_by = db.relationship("User", secondary=user_dislikes_post, backref="user_disliked_posts")

    def create(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def save_changes():
        db.session.commit()

    def __init__(self, post_heading: str, post_text: str, post_created_at: str,
                 post_author: int, post_modified_at=None):
        self.post_heading = post_heading
        self.post_text = post_text
        self.post_author = post_author
        self.post_created_at = post_created_at
        self.post_modified_at = post_modified_at

    def __repr__(self):
        return f"Post({self.post_id} {self.post_heading})"
