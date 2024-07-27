from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.core.otp.base_otp import BaseOTP
from app.models.auth import LoginInput, OTPVerifyPayload
from app.tests.utils.user import init_mfa_tester_user, init_tester_user


def test_login_wrong_credentials(client: TestClient, db: Session):
    tester_user = init_tester_user(db)
    data = LoginInput(email=str(tester_user.email), password="InvalidPassword")
    r = client.post(
        f"{settings.API_V1_STR}/login",
        json=data.model_dump(mode='json'),
    )
    login_response = r.json()
    assert r.status_code == 400
    assert "access_token" not in login_response


def test_login(client: TestClient, db: Session):
    tester_user = init_tester_user(db)
    data = LoginInput(email=tester_user.email,
                      password=settings.TESTER_PWD)
    r = client.post(
        f"{settings.API_V1_STR}/login",
        json=data.model_dump(mode='json'),
    )
    login_response = r.json()
    assert r.status_code == 200
    assert "access_token" in login_response


def test_verify_wrong_otp(client: TestClient, db: Session):
    wrong_otp = "WRONG"
    tester_user = init_mfa_tester_user(db)

    data = OTPVerifyPayload(otp=wrong_otp, user_id=tester_user.id)
    r = client.post(
        f"{settings.API_V1_STR}/otp-verify",
        json=data.model_dump(mode='json'),
    )
    login_response = r.json()
    assert r.status_code == 400
    assert "access_token" not in login_response


def test_verify_otp(client: TestClient, db: Session, otp_generator: BaseOTP):
    tester_user = init_mfa_tester_user(db)
    good_otp = otp_generator.generate(tester_user)

    data = OTPVerifyPayload(otp=good_otp, user_id=tester_user.id)
    r = client.post(
        f"{settings.API_V1_STR}/otp-verify",
        json=data.model_dump(mode='json'),
    )
    login_response = r.json()
    assert r.status_code == 200
    assert "access_token" in login_response


def test_verify_missing_jwt(client: TestClient):
    r = client.get(f"{settings.API_V1_STR}/token-verify")
    assert r.status_code == 403


def test_verify_invalid_jwt(client: TestClient):
    invalid_jwt = "invalid"
    r = client.get(
        f"{settings.API_V1_STR}/token-verify",
        headers={"Authorization": f"Bearer {invalid_jwt}"})
    assert r.status_code == 403


def test_verify_jwt(client: TestClient, db: Session):
    def get_superuser_token_headers(client: TestClient) -> dict[str, str]:
        data = LoginInput(email=settings.TESTER_EMAIL,
                          password=settings.TESTER_PWD)

        r = client.post(f"{settings.API_V1_STR}/login",
                        json=data.model_dump(mode='json'))
        login_response = r.json()
        headers = {"Authorization": f"Bearer {login_response['access_token']}"}
        return headers

    tester_user = init_tester_user(db)
    jwt_header = get_superuser_token_headers(client)
    r = client.get(
        f"{settings.API_V1_STR}/token-verify",
        headers=jwt_header)
    login_response = r.json()
    assert r.status_code == 200
    assert login_response.get("id") == tester_user.id
