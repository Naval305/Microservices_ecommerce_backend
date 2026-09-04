from pickle import NONE

from sqlalchemy.exc import IntegrityError

from app.models.user_model import User
from app.main import db
from app.errors.exceptions import EmailAlreadyExistsError, UserNotFoundError
from app.utils.redis_utility import set_user_active_status


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
    def check_user_existance(email):
        return User.query.filter_by(email=email).first()

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

    def check_user_password_status(self, user, password):
        return user.check_password(password) and user.is_active