
from app.models.core import OTPGenerator

from .otp.base_otp import BaseOTP
from .otp.basic_otp import BasicOTP
from .otp.static import STATIC


def get_generate_otp_instance(otp_generator: OTPGenerator) -> BaseOTP:
    if otp_generator is OTPGenerator.BASIC:
        return BasicOTP()
    elif otp_generator is OTPGenerator.STATIC:
        return STATIC()

    raise Exception("Invalid OTP Generator")
