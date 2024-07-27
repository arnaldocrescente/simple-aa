from datetime import datetime
from typing import Any

from sqlmodel import Session, select

from app.models import UserInDB, UserCreate, User
from app.core.security import get_password_hash, verify_password


def create_user(*, session: Session, data: UserCreate):
    db_obj = UserInDB.model_validate(
        data, update={
            "hashed_pwd": get_password_hash(data.password),
        }
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(UserInDB).where(UserInDB.email == email)
    session_user = session.exec(statement).first()
    return session_user


def get_user_by_id(*, session: Session, user_id: str) -> User | None:
    statement = select(UserInDB).where(UserInDB.id == user_id)
    session_user = session.exec(statement).first()
    return session_user
