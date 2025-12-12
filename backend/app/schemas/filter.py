from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class FilterBase(BaseModel):
    term: str
    is_active: bool = True


class FilterCreate(FilterBase):
    pass


class FilterUpdate(BaseModel):
    term: Optional[str] = None
    is_active: Optional[bool] = None


class FilterResponse(FilterBase):
    id: str
    user_id: str
    created_at: datetime
    match_count: int = 0

    class Config:
        from_attributes = True


class FilterListResponse(BaseModel):
    items: List[FilterResponse]
    total: int
    limit_reached: bool = False
    plan_limit: int


class AlertBase(BaseModel):
    term_id: str
    alert_type: str = "email"
    is_active: bool = True


class AlertCreate(AlertBase):
    pass


class AlertResponse(AlertBase):
    id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True
