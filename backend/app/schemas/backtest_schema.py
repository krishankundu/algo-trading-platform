from pydantic import BaseModel


class BacktestRequest(BaseModel):
    symbol: str
    interval: str
    initial_balance: float


class TradeResult(BaseModel):
    side: str
    entry_price: float
    exit_price: float
    profit: float


class BacktestResponse(BaseModel):
    total_trades: int
    wins: int
    losses: int
    final_balance: float
    roi: float
    trades: list