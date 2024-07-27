from enum import Enum


class MailerErrorType(Enum):
    INVALID_CONFIGURATION_CREDENTIALS = "INVALID_CONFIGURATION_CREDENTIALS"
    INVALID_MAIL_SERVER_URL = "INVALID_MAIL_SERVER_URL"
    SEND_ERROR = "SEND_ERROR"


class MailerException(Exception):
    error_type: MailerErrorType

    def __init__(self, error_type: MailerErrorType):
        self.error_type = error_type

    def error_message(self) -> str:
        if (self.error_type is MailerErrorType.INVALID_CONFIGURATION_CREDENTIALS):
            return f"Invalid SMTP server credentials"
        elif (self.error_type is MailerErrorType.INVALID_MAIL_SERVER_URL):
            return f"Invalid SMTP server url"
        elif (self.error_type is MailerErrorType.SEND_ERROR):
            return f"Error during email sending"
