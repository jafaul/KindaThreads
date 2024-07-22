from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    fullname: str
    nickname: str


class UserCreate(schemas.BaseUserCreate):
    fullname: str
    nickname: str

