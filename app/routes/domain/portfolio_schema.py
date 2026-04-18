from pydantic import BaseModel, Field


class CreatePortfolioRequest(BaseModel):
    username: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    
class PortfolioAccessRequest(BaseModel):
    username: str = Field(..., min_length=1)
    role: str = Field(..., min_length=1)