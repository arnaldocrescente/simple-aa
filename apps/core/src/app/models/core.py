from enum import Enum


class OTPGenerator(Enum):
    BASIC = 'BASIC'
    STATIC = 'STATIC'


class OTPSender(Enum):
    LOG = 'LOG'
    EMAIL = 'EMAIL'
