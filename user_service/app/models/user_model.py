from datetime import datetime

from sqlalchemy.orm import validates
from werkzeug.security import generate_password_hash
from sqlalchemy.orm import Mapped, mapped_column

from app.main import db


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(db.String(30), nullable=False)
    last_name: Mapped[str] = mapped_column(db.String(50), nullable=False)
    email: Mapped[str] = mapped_column(
        db.String(120),
        unique=True,
        nullable=False,
    )
    password_hash: Mapped[str] = mapped_column(
        db.String(255),
        nullable=False,
    )
    date_joined: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True),
        server_default=db.func.now(),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        db.Boolean,
        nullable=False,
        default=True,
    )
    is_staff: Mapped[bool] = mapped_column(
        db.Boolean,
        nullable=False,
        default=False,
    )

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
