from fastapi.testclient import TestClient
import pytest
from sqlmodel import Session, delete
from typing import Generator

from app.core.config import settings
from app.core.db import engine
from app.core.factory_otp_generate import get_generate_otp_instance
from app.core.otp.base_otp import BaseOTP
from app.main import app
from app.models.user import UserInDB


@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
        statement = delete(UserInDB)
        session.exec(statement)
        session.commit()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def otp_generator() -> BaseOTP:
    return get_generate_otp_instance(settings.OTP_GENERATOR)
