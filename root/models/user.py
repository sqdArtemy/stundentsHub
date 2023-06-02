from db_init import db


class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(50), nullable=False)
    user_birthday = db.Column(db.DateTime, nullable=True)
    user_tg_link = db.Column(db.String(200), nullable=True, unique=True)
    user_enrolment_year = db.Column(db.DateTime, nullable=False)
    user_surname = db.Column(db.String(50), nullable=False)
    user_card_id = db.Column(db.String(15), nullable=False)
    user_email = db.Column(db.String(150), unique=True, nullable=False)
    user_phone = db.Column(db.String(50), unique=True, nullable=True)
    user_password = db.Column(db.String(250))
    user_role = db.Column(db.Integer, db.ForeignKey("user_roles.role_id", ondelete="CASCADE"), nullable=False)
    user_university = db.Column(
        db.Integer, db.ForeignKey("universities.university_id", ondelete="CASCADE"), nullable=False
    )
    user_faculty = db.Column(db.Integer, db.ForeignKey("faculties.faculty_id", ondelete="CASCADE"), nullable=True)
    user_posts = db.relationship("Post", backref="author", cascade="all, delete", lazy=True)
    user_comments = db.relationship("Comment", backref="author", cascade="all, delete", lazy=True)

    def create(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def save_changes():
        db.session.commit()

    def __int__(self,
                user_name: str,
                user_surname: str,
                user_email: str,
                user_card_id: str,
                user_birthday: str,
                user_tg_link: str,
                user_enrolment_year: str
                ):
        self.user_name = user_name
        self.user_surname = user_surname
        self.user_email = user_email
        self.user_card_id = user_card_id
        self.user_birthday = user_birthday
        self.user_enrolment_year = user_enrolment_year
        self.user_tg_link = user_tg_link

    def __repr__(self):
        return f"{self.user_name}: {self.user_email}"
