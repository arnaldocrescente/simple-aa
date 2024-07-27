import logging

from typing import Union, List, Dict

from pydantic import EmailStr, HttpUrl

from app.core.config import settings
from app.core.exceptions import MailerException, MailerErrorType

logger = logging.getLogger(__name__)


def send_email(
    *,
    to: Union[EmailStr | List[EmailStr]],
    sender: EmailStr,
    cc: Union[EmailStr | List[EmailStr]] = [],
    ccn: Union[EmailStr | List[EmailStr]] = [],
    subject: str,
    plain_message: str,
    html_message: str = None,
    attachments: Union[HttpUrl | List[HttpUrl]] = [],
) -> None:
    smtp_config = get_smtp_config()

    try:
        logger.info(f"{'*'*40}")
        logger.info(f"{'*'*4} THIS IS A FAKE EMAIL SEND {'*'*4}")
        logger.info(f"{'*'*40}")

        logger.info(f"to: {to}")
        logger.info(f"sender: {sender}")
        logger.info(f"cc: {cc}")
        logger.info(f"ccn: {ccn}")
        logger.info(f"subject: {subject}")
        logger.info(f"{'-'*40}")
        logger.info(f"plain_message: {plain_message}")
        logger.info(f"{'-'*40}")
        logger.info(f"html_message: {html_message}")
        logger.info(f"{'-'*40}")
        logger.info(f"attachments: {attachments}")

        logger.info(f"SMTP configuration: {smtp_config}")
    except Exception as e:
        # ?: FAKE EXCEPTION CHECK
        if e.__str__ == "InvalidCredentials":
            raise MailerException(
                MailerErrorType.INVALID_CONFIGURATION_CREDENTIALS)
        elif e.__str__ == "InvalidUrl":
            raise MailerException(MailerErrorType.INVALID_MAIL_SERVER_URL)
        elif e.__str__ == "EmailSend":
            raise MailerException(MailerErrorType.SEND_ERROR)


def get_smtp_config() -> Dict:
    assert settings.emails_enabled, "no provided configuration for email variables"

    smtp_config = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
    if settings.SMTP_TLS:
        smtp_config["tls"] = True
    elif settings.SMTP_SSL:
        smtp_config["ssl"] = True
    if settings.SMTP_USER:
        smtp_config["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_config["password"] = settings.SMTP_PASSWORD

    return smtp_config
