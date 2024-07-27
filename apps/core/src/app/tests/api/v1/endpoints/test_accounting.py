from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.crud.user import create_user
from app.tests.utils.user import generate_user_data


def test_signup_existing_username(client: TestClient, db: Session):
    user_data = generate_user_data()
    create_user(session=db, data=user_data)
    data = user_data.model_dump()
    r = client.post(
        f"{settings.API_V1_STR}/signup",
        json=data,
    )
    created_user = r.json()
    assert r.status_code == 400
    assert "id" not in created_user


def test_signup(client: TestClient):
    user_data = generate_user_data()
    data = user_data.model_dump()
    r = client.post(
        f"{settings.API_V1_STR}/signup",
        json=data,
    )
    created_user = r.json()
    assert r.status_code == 200
    assert "id" in created_user
