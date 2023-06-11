from db_init import db
import os


class File(db.Model):
    __tablename__ = "files"

    file_id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(256))
    file_url = db.Column(db.String(256))
    file_format = db.Column(db.String(6))
    file_post_id = db.Column(db.Integer, db.ForeignKey("posts.post_id"))

    def create(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __init__(self, file_name: str, file_url):
        self.file_name = file_name
        self.file_url = file_url
        self.file_format = os.path.splitext(file_name)[1]

    def __repr__(self):
        return self.file_name
