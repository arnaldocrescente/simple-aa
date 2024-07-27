import logging
import requests

from app.core.config import settings

logger = logging.getLogger(__name__)

if not settings.MAILER_URL:
    raise EnvironmentError("MAILER_URL is not defined.")


def send_email(*,
               to: str,
               cc: str | list[str] = [],
               ccn: str | list[str] = [],
               subject: str,
               plain_message: str,
               html_message: str = None,
               attachments: str | list[str] = [],):
    send_email_url = f"{settings.MAILER_URL}/send-email"
    params = dict(
        to=to,
        sender=settings.SERVER_EMAIL,
        cc=cc,
        ccn=ccn,
        subject=subject,
        plain_message=plain_message,
        html_message=html_message,
        attachments=attachments,
    )
    response = requests.post(send_email_url, json=params)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(
            f"Failed to send the email: {response.status_code}, {response.text}")
