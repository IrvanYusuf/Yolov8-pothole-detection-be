from sqlmodel import Field,  SQLModel
import uuid


class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(index=True)
    password: str = Field(default=None)
    age: int = Field(default=None, index=True)
    email: str
    address: str
