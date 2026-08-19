from pydantic import BaseModel
from datetime import datetime

class CommodityOut(BaseModel):
    id: int
    canonical_name: str
    original_name: str
    commodity_group: str
    unit: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
