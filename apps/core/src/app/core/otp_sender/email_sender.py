import requests

from app.models.user import User
from app.core.mailer_service import send_email

from .base_sender import BaseOTPSender


class EmailOTPSender(BaseOTPSender):

    def getSubject(self) -> str:
        return 'OTP from Simple-AA'

    def getPlainMessage(self, otp: str, receiver: User) -> str:
        # TODO: Use Jinja template
        return f'Hi {receiver.first_name}. This is your OTP: {otp}.'

    def getHtmlMessage(self, otp: str, receiver: User) -> str:
        # TODO: Use Jinja template
        return f'<p>Hi {receiver.first_name}. This is your OTP: <b>{otp}</b>.</p>'

    async def send(self, otp: str, receiver: User):
        send_email(to=str(receiver.email), subject=self.getSubject(),
                   plain_message=self.getPlainMessage(otp, receiver),
                   html_message=self.getHtmlMessage(otp, receiver))
