from fastapi import APIRouter, HTTPException

from app.schema.mailer import SendEmailRequest, SendEmailResponse
from app.core.email_service import send_email

from app.core.exceptions import MailerException

router = APIRouter()


@router.post("/send-email")
def signup(data: SendEmailRequest) -> SendEmailResponse:
    """
    Send an email
    """
    try:
        send_email(
            to=data.to,
            sender=data.sender,
            cc=data.cc,
            ccn=data.ccn,
            subject=data.subject,
            plain_message=data.plain_message,
            html_message=data.html_message,
            attachments=data.attachments,
        )
    except MailerException as e:
        raise HTTPException(500, e.error_message())

    return SendEmailResponse(status="SENT")
