import secrets
from typing import Annotated, List, Union

from pydantic import AnyUrl, BeforeValidator, computed_field
from pydantic_settings import BaseSettings


def assemble_cors_origins(v: str) -> Union[List[str], str]:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, (list, str)):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    BACKEND_CORS_ORIGINS: Annotated[
        List[AnyUrl] | AnyUrl, BeforeValidator(assemble_cors_origins)
    ] = []
    PROJECT_NAME: str

    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None

    @computed_field
    @property
    def emails_enabled(self) -> bool:
        return bool(True)  # Change when implement a real email send

    class Config:
        case_sensitive = True


settings = Settings()
