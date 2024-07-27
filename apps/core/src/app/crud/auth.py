from sqlmodel import Session

from app.core.config import settings
from app.core.factory_otp_generate import get_generate_otp_instance
from app.core.security import verify_password
from app.models import User

from .user import get_user_by_email, get_user_by_id


OTPGenerator = get_generate_otp_instance(settings.OTP_GENERATOR)


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_pwd):
        return None
    return User(**db_user.model_dump())


def mfa_authenticate(*, session: Session, user_id: str, otp: str) -> User | None:
    db_user = get_user_by_id(session=session, user_id=user_id)
    if not db_user:
        return None
    if OTPGenerator.generate(db_user) != otp:
        return None
    return User(**db_user.model_dump())
