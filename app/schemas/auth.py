from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class UserRegister(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class Token(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sub: str
    exp: int
    role: UserRole
