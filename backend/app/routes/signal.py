from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from app.database.connection import SessionLocal

from app.database.models import User, Strategy, Trade

from app.database.portfolio_model import Portfolio

from app.database.holding_model import Holding

from app.utils.jwt_handler import verify_token

from app.services.signal_engine import evaluate_strategy_signal


router = APIRouter(
    prefix="/signal",
    tags=["Signals"]
)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


def execute_trigger_trade(

    db: Session,

    user: User,

    strategy: Strategy,

    signal: str,

    price: float

):

    portfolio = db.query(Portfolio).filter(
        Portfolio.user_id == user.id
    ).first()

    if not portfolio:

        return {
            "executed": False,
            "message": "Portfolio not found"
        }

    quantity = strategy.order_quantity or 1

    if quantity <= 0:

        quantity = 1

    total_cost = price * quantity

    holding = db.query(Holding).filter(
        Holding.user_id == user.id,
        Holding.symbol == strategy.symbol
    ).first()

    # BUY
    if signal == "BUY":

        if portfolio.balance < total_cost:

            return {
                "executed": False,
                "message": "Insufficient balance"
            }

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

        return {
            "executed": True,
            "message": "BUY trigger executed"
        }

    # SELL
    if signal == "SELL":

        if not holding or holding.quantity < quantity:

            return {
                "executed": False,
                "message": "Insufficient holdings"
            }

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

        return {
            "executed": True,
            "message": "SELL trigger executed"
        }

    return {
        "executed": False,
        "message": "No executable signal"
    }


@router.get("/all")
def get_all_strategy_signals(

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

    strategies = db.query(Strategy).filter(
        Strategy.owner_id == user.id
    ).all()

    results = []

    for strategy in strategies:

        result = evaluate_strategy_signal(strategy)

        signal = result["signal"]

        trigger_result = {
            "executed": False,
            "message": "Trigger disabled"
        }

        if strategy.trigger_enabled:

            if signal in ["BUY", "SELL"]:

                if strategy.last_signal != signal:

                    trigger_result = execute_trigger_trade(
                        db=db,
                        user=user,
                        strategy=strategy,
                        signal=signal,
                        price=result["price"]
                    )

                    if trigger_result["executed"]:

                        strategy.last_signal = signal

                        strategy.trigger_enabled = False

                else:

                    trigger_result = {
                        "executed": False,
                        "message": "Signal already triggered"
                    }

            elif signal == "WAIT":

                strategy.last_signal = "WAIT"

                trigger_result = {
                    "executed": False,
                    "message": "Signal is WAIT. Trigger remains armed"
                }

        result["trigger_enabled"] = strategy.trigger_enabled

        result["order_quantity"] = strategy.order_quantity

        result["last_signal"] = strategy.last_signal

        result["trigger_result"] = trigger_result

        results.append(result)

    db.commit()

    return results