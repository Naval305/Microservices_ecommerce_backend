from datetime import datetime

from sqlalchemy.orm import validates
from werkzeug.security import generate_password_hash

from ..main import db


class User(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    first_name: str = db.Column(db.String(30), nullable=False)
    last_name: str = db.Column(db.String(50), nullable=False)
    email: str = db.Column(db.String(120), unique=True, nullable=False)
    password_hash: str = db.Column(db.String(255), nullable=False)
    date_joined: datetime = db.Column(
        db.DateTime(timezone=True),
        server_default=db.func.now(),
        nullable=False,
    )
    is_active: bool = db.Column(db.Boolean, nullable=False, default=True)
    is_staff: bool = db.Column(db.Boolean, nullable=False, default=False)

    @validates("email")
    def normalize_email(self, key: str, value: str) -> str:
        if value:
            return value.strip().lower()
        return value

    # Define a property for the full name
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def set_password(self, password: str) -> None:
        self.password_hash: str = generate_password_hash(str(password))
