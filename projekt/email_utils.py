# email.py

from flask_mail import Message
from flask import current_app
from . import mail
from .tokens import generate_reset_token
from flask import url_for

def send_email(to, subject, template):
    with current_app.app_context():
   
        msg = Message(
            subject,
            recipients=[to],
            html=template,
            sender=current_app.config["MAIL_DEFAULT_SENDER"],
        )
        mail.send(msg)

def send_password_reset_email(user):
    token = generate_reset_token(user.email)
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    subject = "Password Reset Request"
    template = f"Click the following link to reset your password: {reset_url}"
    send_email(user.email, subject, template)