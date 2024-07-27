from datetime import timedelta
from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.api_v1.deps import AuthUser, SessionDep
from app.core.config import settings
from app.core import security
from app.crud.auth import authenticate, mfa_authenticate
from app.models import LoginInput, Token, OTPVerifyPayload
from app.core.factory_otp_sender import get_sender_otp_instance
from app.core.factory_otp_generate import get_generate_otp_instance

router = APIRouter()

OTPSender = get_sender_otp_instance(settings.OTP_SENDER)
OTPGenerator = get_generate_otp_instance(settings.OTP_GENERATOR)


@router.post("/login")
async def login(
    session: SessionDep, data: LoginInput
) -> Any:
    """
    Authenticates users using their credentials. If 2FA is enabled, an OTP will be sent.
    """
    user = authenticate(
        session=session, email=data.email, password=data.password
    )
    if not user:
        raise HTTPException(
            status_code=400, detail="Incorrect email or password")

    if user.mfa_enabled:
        await OTPSender.send(OTPGenerator.generate(user), user)
        return {'status': 'OTP sent!'}

    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_access_token(
            user.id, expires_delta=access_token_expires
        )
    )


@router.post("/otp-verify")
def otp_verify(
    session: SessionDep, data: OTPVerifyPayload
) -> Any:
    """
    Validates the OTP sent to the user's email for accounts with 2FA enabled.
    """
    user = mfa_authenticate(
        session=session, user_id=data.user_id, otp=data.otp
    )
    if not user:
        raise HTTPException(
            status_code=400, detail="Expired or invalid OTP")

    if user.mfa_enabled is False:
        raise HTTPException(
            status_code=400, detail="You should enable MFA before verify an OTP.")

    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_access_token(
            user.id, expires_delta=access_token_expires
        )
    )


@ router.get("/token-verify")
def token_verify(
    current_user: AuthUser
) -> Any:
    """
    Test access token
    """
    return current_user
