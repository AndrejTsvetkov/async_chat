from pydantic import BaseModel


class RegisterValidator(BaseModel):
    username: str


class History(BaseModel):
    messages: list[str]
