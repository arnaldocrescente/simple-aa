from datetime import datetime
from typing import Optional
from uuid import uuid4

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    first_name: Optional[str] = Field(default=None, max_length=255)
    last_name: Optional[str] = Field(default=None, max_length=255)
    mfa_enabled: bool = Field(default=False, nullable=False)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)
    password_confirm: str = Field(min_length=8, max_length=40)


class UserInDBBase(UserBase):
    id: str = Field(default_factory=uuid4, primary_key=True)
    created: datetime = Field(default_factory=datetime.now, nullable=False)


class UserInDB(UserInDBBase, table=True):

    __tablename__: str = "user"

    hashed_pwd: str


class User (UserInDBBase):
    pass
