from sqlalchemy.exc import IntegrityError

from app.models.user_model import User
from app.main import db
from app.errors.exceptions import EmailAlreadyExistsError


class UserService:

    def __init__(self) -> None:
        pass

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

        return new_user.id

    def check_user_password(self, user, password):
        return user.check_password(password)

    @staticmethod
    def is_staff(email):
        user = UserService().check_user_existance(email)
        return user.is_staff if user else False