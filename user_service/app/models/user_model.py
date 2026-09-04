from sqlalchemy.orm import validates
from werkzeug.security import generate_password_hash

from ..main import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    date_joined = db.Column(
        db.DateTime(timezone=True),
        server_default=db.func.now(),
        nullable=False,
    )
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    is_staff = db.Column(db.Boolean, nullable=False, default=False)
    # fb_token = db.Column(db.String(100), nullable=True)
    # twitter_token = db.Column(db.String(100), nullable=True)
    # google_token = db.Column(db.String(100), nullable=True)

    @validates("email")
    def normalize_email(self, key, value):
        if value:
            return value.strip().lower()
        return value

    # Define a property for the full name
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def set_password(self, password):
        self.password_hash = generate_password_hash(str(password))
