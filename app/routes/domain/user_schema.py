from pydantic import BaseModel, Field


class CreateUserRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
    firstname: str = Field(..., min_length=1)
    lastname: str = Field(..., min_length=1)
    balance: float = Field(..., ge=0)


class UpdateUserBalanceRequest(BaseModel):
    username: str = Field(..., min_length=1)
    new_balance: float = Field(..., ge=0)