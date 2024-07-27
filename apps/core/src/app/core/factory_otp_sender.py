

from app.models.core import OTPSender

from .otp_sender.base_sender import BaseOTPSender
from .otp_sender.log_sender import LogOTPSender
from .otp_sender.email_sender import EmailOTPSender


def get_sender_otp_instance(otp_sender: OTPSender) -> BaseOTPSender:
    if otp_sender is OTPSender.LOG:
        return LogOTPSender()
    elif otp_sender is OTPSender.EMAIL:
        return EmailOTPSender()

    raise Exception("Invalid OTP Sender")
