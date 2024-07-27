from app.models.user import User

from .base_otp import BaseOTP


class STATIC(BaseOTP):
    def generate(self, user: User):
        return "123456"
