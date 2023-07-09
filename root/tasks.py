import http_codes
from flask_mail import Message
from flask_restful import abort
from celery import shared_task
from typing import List
from app_init import mail, celery


@shared_task(bind=True)
def send_mail(self, recipients: List[str], subject: str, body: str, *args, **kwargs):
    message = Message(
        subject=subject,
        recipients=recipients,
        body=body,
        sender="noreply@studenthub.com"
    )

    try:
        mail.send(message)
    except Exception as e:
        abort(http_codes.HTTP_BAD_REQUEST_400, error_message=str(e))

    return "Done"
