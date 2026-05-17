from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.database.models import Trade
from app.database.portfolio_model import Portfolio
from app.database.holding_model import Holding
from app.services.signal_engine import evaluate_strategy_signal
from app.database.models import Strategy, User

from app.schemas.strategy_schema import (
    StrategyCreate,
    StrategyResponse
)

from app.utils.jwt_handler import verify_token

router = APIRouter(
    prefix="/strategy",
    tags=["Strategies"]
)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.post("/create")
def create_strategy(

    strategy: StrategyCreate,

    token: str,

    db: Session = Depends(get_db)

):

    # VALIDATION
    if (
        not strategy.name.strip()
        or not strategy.symbol.strip()
        or not strategy.timeframe.strip()
    ):

        raise HTTPException(
            status_code=400,
            detail="All fields are required"
        )

    payload = verify_token(token)

    email = payload.get("sub")

    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    new_strategy = Strategy(

        name=strategy.name,

        symbol=strategy.symbol,

        timeframe=strategy.timeframe,

        strategy_type=strategy.strategy_type,

        buy_condition=strategy.buy_condition,

        sell_condition=strategy.sell_condition,

        trigger_enabled=strategy.trigger_enabled,

        order_quantity=strategy.order_quantity,

        last_signal="WAIT",

        owner_id=user.id
    )

    db.add(new_strategy)

    db.commit()

    db.refresh(new_strategy)

    return {
        "message": "Strategy created",
        "strategy": new_strategy
    }

@router.get("/all")
def get_strategies(
    token: str,
    db: Session = Depends(get_db)
):
    payload = verify_token(token)

    user = db.query(User).filter(
        User.email == payload["sub"]
    ).first()

    strategies = db.query(Strategy).filter(
        Strategy.owner_id == user.id
    ).all()

    return strategies


@router.delete("/delete/{strategy_id}")

def delete_strategy(

    strategy_id: int,

    token: str,

    db: Session = Depends(get_db)

):

    payload = verify_token(token)

    email = payload.get("sub")

    user = db.query(User).filter(
        User.email == email
    ).first()

    strategy = db.query(Strategy).filter(

        Strategy.id == strategy_id,

        Strategy.owner_id == user.id

    ).first()

    if not strategy:

        raise HTTPException(
            status_code=404,
            detail="Strategy not found"
        )

    db.delete(strategy)

    db.commit()

    return {
        "message": "Strategy deleted"
    }

@router.put("/trigger/{strategy_id}")
def update_strategy_trigger(

    strategy_id: int,

    trigger_enabled: bool,

    order_quantity: float,

    token: str,

    db: Session = Depends(get_db)

):

    payload = verify_token(token)

    user = db.query(User).filter(
        User.email == payload["sub"]
    ).first()

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    strategy = db.query(Strategy).filter(
        Strategy.id == strategy_id,
        Strategy.owner_id == user.id
    ).first()

    if not strategy:

        raise HTTPException(
            status_code=404,
            detail="Strategy not found"
        )

    if order_quantity <= 0:

        raise HTTPException(
            status_code=400,
            detail="Order quantity must be greater than zero"
        )

    strategy.order_quantity = order_quantity

    # If user is unchecking manually, only save disabled state.
    if not trigger_enabled:

        strategy.trigger_enabled = False

        db.commit()

        db.refresh(strategy)

        return {
            "message": "Trigger disabled",
            "executed": False,
            "signal": "WAIT",
            "strategy": {
                "id": strategy.id,
                "name": strategy.name,
                "trigger_enabled": strategy.trigger_enabled,
                "order_quantity": strategy.order_quantity,
                "last_signal": strategy.last_signal
            }
        }

    # =========================
    # ONE-SHOT TRIGGER LOGIC
    # =========================

    signal_result = evaluate_strategy_signal(strategy)

    signal = signal_result["signal"]

    price = signal_result.get("price")

    executed = False

    execution_message = "No trade executed"

    portfolio = db.query(Portfolio).filter(
        Portfolio.user_id == user.id
    ).first()

    if not portfolio:

        raise HTTPException(
            status_code=404,
            detail="Portfolio not found"
        )

    quantity = order_quantity

    if signal in ["BUY", "SELL"] and price:

        total_cost = price * quantity

        holding = db.query(Holding).filter(
            Holding.user_id == user.id,
            Holding.symbol == strategy.symbol
        ).first()

        # =========================
        # BUY EXECUTION
        # =========================

        if signal == "BUY":

            if portfolio.balance < total_cost:

                execution_message = "Insufficient balance"

            else:

                portfolio.balance -= total_cost

                if holding:

                    old_quantity = holding.quantity

                    old_average_price = holding.average_price

                    new_quantity = old_quantity + quantity

                    new_average_price = (
                        (old_quantity * old_average_price) + total_cost
                    ) / new_quantity

                    holding.quantity = new_quantity

                    holding.average_price = new_average_price

                else:

                    holding = Holding(
                        user_id=user.id,
                        symbol=strategy.symbol,
                        quantity=quantity,
                        average_price=price
                    )

                    db.add(holding)

                trade = Trade(
                    symbol=strategy.symbol,
                    side="BUY",
                    price=price,
                    quantity=quantity,
                    pnl=0,
                    owner_id=user.id
                )

                db.add(trade)

                executed = True

                execution_message = "BUY trigger executed"

        # =========================
        # SELL EXECUTION
        # =========================

        elif signal == "SELL":

            if not holding or holding.quantity < quantity:

                execution_message = "Insufficient holdings"

            else:

                trade_pnl = (price - holding.average_price) * quantity

                portfolio.balance += total_cost

                portfolio.realized_pnl += trade_pnl

                holding.quantity -= quantity

                if holding.quantity <= 0:

                    db.delete(holding)

                trade = Trade(
                    symbol=strategy.symbol,
                    side="SELL",
                    price=price,
                    quantity=quantity,
                    pnl=trade_pnl,
                    owner_id=user.id
                )

                db.add(trade)

                executed = True

                execution_message = "SELL trigger executed"

    elif signal == "WAIT":

        execution_message = "Signal is WAIT. Trigger is armed"

    if executed:

        strategy.trigger_enabled = False

        strategy.last_signal = signal

    elif signal == "WAIT":

        strategy.trigger_enabled = True

        strategy.last_signal = "WAIT"

    else:

        strategy.trigger_enabled = False

        strategy.last_signal = signal

    db.commit()

    db.refresh(strategy)

    return {
        "message": execution_message,
        "executed": executed,
        "signal": signal,
        "price": price,
        "strategy": {
            "id": strategy.id,
            "name": strategy.name,
            "symbol": strategy.symbol,
            "strategy_type": strategy.strategy_type,
            "trigger_enabled": strategy.trigger_enabled,
            "order_quantity": strategy.order_quantity,
            "last_signal": strategy.last_signal
        }
    }