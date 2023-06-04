from db_init import db
from datetime import datetime


class Comment(db.Model):
    __tablename__ = "comments"

    comment_id = db.Column(db.Integer, primary_key=True)
    comment_text = db.Column(db.String(500), nullable=False)
    comment_created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    comment_modified_at = db.Column(db.DateTime, nullable=True, default=None)
    comment_author = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    comment_post = db.Column(db.Integer, db.ForeignKey("posts.post_id", ondelete="CASCADE"), nullable=False)

    def create(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def save_changes():
        db.session.commit()

    def __init__(self, comment_text: str, comment_created_at: str, comment_author: int,
                 comment_post: int, comment_modified_at=None):
        self.comment_text = comment_text
        self.comment_author = comment_author
        self.comment_post = comment_post
        self.comment_created_at = comment_created_at
        self.comment_modified_at = comment_modified_at

    def __repr__(self):
        return f"Comment by {self.comment_author} under the post {self.comment_post })"
