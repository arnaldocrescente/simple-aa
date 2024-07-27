from datetime import timedelta

from app.core.security import (
    get_password_hash, verify_password, create_access_token, decode_jwt)


def test_password():
    password = "mypassword"
    hashed_password = get_password_hash(password)

    assert verify_password(password, hashed_password)


def test_jwt_payload():
    jwt_expiration = timedelta(minutes=2)
    subject = "mySubject"

    jwt = create_access_token(subject, jwt_expiration, {
                              "check": "extra field"})
    decoded_jwt = decode_jwt(jwt)

    assert "exp" in decoded_jwt
    assert "sub" in decoded_jwt
    assert "check" in decoded_jwt
