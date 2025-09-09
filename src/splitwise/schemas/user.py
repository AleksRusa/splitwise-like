from pydantic import BaseModel, ConfigDict


class Token(BaseModel):
    access_token: str
    token_type: str


class UserCreate(BaseModel):
    email: str
    password: str


class UserDTO(BaseModel):
    email: str
    password: str


class UserId(BaseModel):
    id: int


class UserOut(BaseModel):
    email: str

    model_config = ConfigDict(from_attributes=True)
