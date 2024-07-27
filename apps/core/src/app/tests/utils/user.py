from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.models.user import UserCreate, UserInDB
from app.crud.user import create_user, get_user_by_email

from .utils import random_lower_string, random_email


def generate_user_data(mfa_enabled=False) -> UserCreate:
    password = random_lower_string()
    return UserCreate(
        email=random_email(),
        first_name=random_lower_string(8),
        last_name=random_lower_string(8),
        mfa_enabled=mfa_enabled,
        password=password,
        password_confirm=password

    )


def init_tester_user(db: Session) -> UserInDB | None:
    user = get_user_by_email(session=db, email=settings.TESTER_EMAIL)

    if user is not None:
        return user

    tester_user = UserCreate(
        email=settings.TESTER_EMAIL,
        first_name="Tester",
        last_name="User",
        mfa_enabled=False,
        password=settings.TESTER_PWD,
        password_confirm=settings.TESTER_PWD
    )

    return create_user(session=db, data=tester_user)


def init_mfa_tester_user(db: Session) -> UserInDB | None:
    user_email = settings.TESTER_EMAIL + "mfa"
    user = get_user_by_email(session=db, email=user_email)

    if user is not None:
        return user

    tester_user = UserCreate(
        email=user_email,
        first_name="Tester",
        last_name="User",
        mfa_enabled=True,
        password=settings.TESTER_PWD,
        password_confirm=settings.TESTER_PWD
    )

    return create_user(session=db, data=tester_user)
