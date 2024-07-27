from enum import Enum
import secrets
from typing import Annotated, List, Optional, Union

from pydantic import AnyUrl, BeforeValidator, PostgresDsn, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings

from app.models.core import OTPGenerator, OTPSender


def assemble_cors_origins(v: str) -> Union[List[str], str]:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, (list, str)):
        return v
    raise ValueError(v)


def parse_otp_sender(v: str) -> Optional[str]:
    try:
        return OTPSender[v]
    except KeyError:
        return OTPSender.FAKE


def parse_otp_generator(v: str) -> Optional[str]:
    try:
        return OTPGenerator[v]
    except KeyError:
        return OTPGenerator.BASIC


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 2
    BACKEND_CORS_ORIGINS: Annotated[
        List[AnyUrl] | AnyUrl, BeforeValidator(assemble_cors_origins)
    ] = []
    PROJECT_NAME: str
    OTP_GENERATOR: Annotated[
        OTPGenerator, BeforeValidator(parse_otp_generator)
    ]
    OTP_SENDER: Annotated[
        OTPSender, BeforeValidator(parse_otp_sender)
    ]

    SERVER_EMAIL: str
    MAILER_URL: str | None = None

    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str = ""

    @computed_field  # type: ignore[misc]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    TESTER_EMAIL: str = 'tester@simpleaa.com'
    TESTER_PWD: str = 'testerP4ssword'

    class Config:
        case_sensitive = True


settings = Settings()
