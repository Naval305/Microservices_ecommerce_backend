from pickle import NONE

from sqlalchemy.exc import IntegrityError

from app.models.user_model import User
from app.main import db
from app.errors.exceptions import EmailAlreadyExistsError, UserNotFoundError
from app.services.user_status_service import set_user_active_status
from werkzeug.security import generate_password_hash, check_password_hash

DUMMY_PASSWORD_HASH = generate_password_hash("not-a-real-password")

class UserContext:

    def __init__(self, user_id=None) -> None:
        self.user_id = user_id
        self._user = None

    @property
    def user(self):
        if self._user is None:
            self._user = db.session.get(User, self.user_id)
            if self._user is None:
                raise UserNotFoundError("User not found")
        return self._user

    @staticmethod
    def get_users(page, per_page):
        return User.query.paginate(
            page=page,
            per_page=per_page,
            error_out=False,
        )

    @staticmethod
    def create_user(first_name, last_name, email, password):
        new_user = User(
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
            raise EmailAlreadyExistsError()

        set_user_active_status(new_user.id, new_user.is_active)
        return new_user.id

    def check_user_existance(self, email):
        self._user = User.query.filter_by(email=email).first()
        return self._user

    def check_user_password_status(self, password):
        hash_to_check = self._user.password_hash if self._user else DUMMY_PASSWORD_HASH
        password_ok = check_password_hash(hash_to_check, password)
        return bool(self._user) and self._user.is_active and password_ok