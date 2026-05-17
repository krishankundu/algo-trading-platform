from pydantic import BaseModel
from typing import Optional

class StrategyCreate(BaseModel):

    name: str

    symbol: str

    timeframe: str
    
    strategy_type: str

    buy_condition: str

    sell_condition: str

    trigger_enabled: Optional[bool] = False

    order_quantity: Optional[float] = 1


class StrategyResponse(BaseModel):

    id: int

    name: str

    symbol: str

    timeframe: str

    owner_id: int

    class Config:

        from_attributes = True