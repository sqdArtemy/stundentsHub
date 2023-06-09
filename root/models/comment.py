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
    comment_parent = db.Column(db.Integer, db.ForeignKey("comments.comment_id", ondelete="CASCADE"), nullable=True)
    comment_child = db.relationship("Comment", backref=db.backref("parent_comment", remote_side="Comment.comment_id"),
                                    cascade="all, delete", lazy=True)
    comment_image_id = db.Column(db.Integer, db.ForeignKey("files.file_id", ondelete="CASCADE"), nullable=True)
    comment_image = db.relationship("File", backref="uploaded_in_comment", cascade="all, delete", lazy=True)

    def create(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def save_changes():
        db.session.commit()

    def __init__(self, comment_text: str, comment_created_at: str, comment_post: int,
                 author, parent_comment, comment_image=None, comment_modified_at=None, comment_parent=None):
        self.comment_text = comment_text
        self.comment_author = author.user_id
        self.comment_post = comment_post
        self.comment_created_at = comment_created_at
        self.comment_modified_at = comment_modified_at
        self.comment_parent = comment_parent
        self.author = author
        self.parent_comment = parent_comment
        if comment_image:
            self.comment_image = comment_image
            self.comment_image_id = comment_image.file_id

    def __repr__(self):
        return f"Comment by {self.comment_author} under the post {self.comment_post })"
