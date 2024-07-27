from fastapi import APIRouter, HTTPException

from app.api.api_v1.deps import SessionDep
from app.models.user import UserCreate, User
from app.crud.user import create_user, get_user_by_email


router = APIRouter()


@router.post("/signup")
def signup(
    session: SessionDep, data: UserCreate
) -> User:
    """
    User signup
    """
    user = get_user_by_email(session=session, email=data.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

    if data.password != data.password_confirm:
        raise HTTPException(
            status_code=400,
            detail="Password differ to confirm password",
        )
    user = create_user(session=session, data=data)
    return user
