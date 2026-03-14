from pydantic import BaseModel, Field


class BuyTradeRequest(BaseModel):
    portfolio_id: int = Field(..., gt=0)
    ticker: str = Field(..., min_length=1)
    quantity: float = Field(..., gt=0)


class SellTradeRequest(BaseModel):
    portfolio_id: int = Field(..., gt=0)
    ticker: str = Field(..., min_length=1)
    quantity: float = Field(..., gt=0)
    sale_price: float = Field(..., gt=0)