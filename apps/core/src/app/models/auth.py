from pydantic import EmailStr, BaseModel


class LoginInput(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(BaseModel):
    sub: str | None = None


class OTPVerifyPayload(BaseModel):
    otp: str
    user_id: str
