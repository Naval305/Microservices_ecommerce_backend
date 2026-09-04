from flask_sqlalchemy.pagination import Pagination
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from app.errors.exceptions import EmailAlreadyExistsError, UserNotFoundError
from app.main import db
from app.models.user_model import User
from app.services.user_status_service import set_user_active_status

DUMMY_PASSWORD_HASH: str = generate_password_hash("not-a-real-password")


class UserContext:
    def __init__(self, user_id: int| str | None = None) -> None:
        self.user_id: int | str | None = user_id
        self._user: User | None = None

    @property
    def user(self) -> User:
        if self._user is None:
            self._user: User | None = db.session.get(User, self.user_id)
            if self._user is None:
                raise UserNotFoundError("User not found")
        return self._user

    @staticmethod
    def get_users(page: int, per_page: int) -> Pagination:
        return User.query.paginate(
            page=page,
            per_page=per_page,
            error_out=False,
        )

    @staticmethod
    def create_user(first_name: str, last_name: str, email: str, password: str) -> int:
        new_user: User = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
        )
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise EmailAlreadyExistsError() from None

        set_user_active_status(new_user.id, new_user.is_active)
        return new_user.id

    def check_user_existance(self, email: str) -> User | None:
        self._user: User | None = User.query.filter_by(email=email).first()
        return self._user

    def check_user_password_status(self, password: str) -> bool:
        hash_to_check: str = self._user.password_hash if self._user else DUMMY_PASSWORD_HASH
        password_ok: bool = check_password_hash(hash_to_check, password)
        return bool(self._user) and self._user.is_active and password_ok
