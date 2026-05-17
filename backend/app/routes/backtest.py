from fastapi import APIRouter

from app.schemas.backtest_schema import (
    BacktestRequest
)

from app.services.backtest_service import (
    run_backtest
)

router = APIRouter(
    prefix="/backtest",
    tags=["Backtest"]
)


@router.post("/run")
def run_backtest_api(
    request: BacktestRequest
):

    result = run_backtest(
        request.symbol,
        request.interval,
        request.initial_balance
    )

    return result