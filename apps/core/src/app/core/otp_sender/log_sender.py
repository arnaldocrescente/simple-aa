import logging

from app.models.user import User

from .base_sender import BaseOTPSender

logger = logging.getLogger(__name__)


class LogOTPSender(BaseOTPSender):
    def send(self, otp: str, receiver: User):
        logger.info(f"{'#'*6} OTP for {receiver.email} -> {otp}")
