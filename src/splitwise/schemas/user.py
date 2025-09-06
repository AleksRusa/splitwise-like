from pydantic import BaseModel, ConfigDict


class Token(BaseModel):
    access_token: str
    token_type: str
    access_token_expires: str


class UserCreate(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    login: str
    email: str

    model_config = ConfigDict(from_attributes=True)
