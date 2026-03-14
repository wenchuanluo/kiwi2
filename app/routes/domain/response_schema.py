from pydantic import BaseModel
from typing import Any, Optional

class ApiErrorResponse(BaseModel):
    error: str
    detail: Optional[Any] = None