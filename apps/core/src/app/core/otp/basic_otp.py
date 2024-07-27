import math
import random
import string
from time import time

from app.models.user import User

from .base_otp import BaseOTP


class BasicOTP(BaseOTP):

    def get_random(self, user_secret: string, length=6) -> str:
        """Generate different OTP each 100 seconds

        Args:
            length (int, optional): the otp length. Defaults to 6.

        Returns:
            str: OTP generated
        """
        seed = math.floor(time()/100)
        random.seed(f"{user_secret}{seed}")
        return "".join([random.choice(string.digits) for _ in range(length)])

    def generate(self, user: User):
        return self.get_random(user.id)
