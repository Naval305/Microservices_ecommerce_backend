from flask_mail import Message
from app.extensions.extensions import mail
from flask import render_template
from flask import current_app

from app.extensions.celery_connection import celery_app


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def send_welcome_email(self, user_email, first_name) -> None:
    try:
        if not current_app.config["SEND_EMAILS"]:
            return
        msg = Message(
            subject="Welcome to YourApp!",
            recipients=[user_email],
            html=f"""
                <h1>Welcome, {first_name}!</h1>
                <p>Thanks for joining us.</p>
            """,
        )
        mail.send(msg)
    except Exception as exc:
        # retry on transient failures (SMTP timeout etc.)
        raise self.retry(exc=exc)