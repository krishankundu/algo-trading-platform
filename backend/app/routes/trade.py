from fastapi import APIRouter, Depends, HTTPException
import yfinance as yf
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal

from app.database.models import Trade, User

from app.database.portfolio_model import Portfolio

from app.database.holding_model import Holding

from app.utils.jwt_handler import verify_token

import requests

router = APIRouter(
    prefix="/trade",
    tags=["Trades"]
)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()

YAHOO_SYMBOL_MAP = {
    "BTCUSDT": "BTC-USD",
    "ETHUSDT": "ETH-USD",
    "BNBUSDT": "BNB-USD",
    "SOLUSDT": "SOL-USD",
    "XRPUSDT": "XRP-USD",
    "ADAUSDT": "ADA-USD",
}


def get_live_price(symbol: str):

    symbol = symbol.upper()

    yahoo_symbol = YAHOO_SYMBOL_MAP.get(symbol)

    if not yahoo_symbol:

        raise HTTPException(
            status_code=400,
            detail="Unsupported symbol"
        )

    ticker = yf.Ticker(yahoo_symbol)

    price = ticker.fast_info.get("last_price")

    if price is None:

        history = ticker.history(period="1d", interval="1m")

        if history.empty:

            raise HTTPException(
                status_code=400,
                detail="Price fetch failed"
            )

        price = history["Close"].iloc[-1]

    return float(price)


@router.post("/create")
def create_trade(

    symbol: str,

    side: str,

    price: float,

    quantity: float,

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

    portfolio = db.query(Portfolio).filter(
        Portfolio.user_id == user.id
    ).first()

    if not portfolio:

        raise HTTPException(
            status_code=404,
            detail="Portfolio not found"
        )

    side = side.upper()

    live_price = get_live_price(symbol)

    price = live_price

    total_cost = price * quantity

    holding = db.query(Holding).filter(
        Holding.user_id == user.id,
        Holding.symbol == symbol
    ).first()

    # =========================
    # BUY LOGIC
    # =========================

    if side == "BUY":

        if portfolio.balance < total_cost:

            raise HTTPException(
                status_code=400,
                detail="Insufficient balance"
            )

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
                symbol=symbol,
                quantity=quantity,
                average_price=price
            )

            db.add(holding)

    # =========================
    # SELL LOGIC
    # =========================

    elif side == "SELL":

        if not holding or holding.quantity < quantity:

            raise HTTPException(
                status_code=400,
                detail="Insufficient holdings"
            )

        portfolio.balance += total_cost

        trade_pnl = (price - holding.average_price) * quantity

        portfolio.realized_pnl += trade_pnl

        holding.quantity -= quantity

        if holding.quantity == 0:

            db.delete(holding)

    else:

        raise HTTPException(
            status_code=400,
            detail="Invalid trade side"
        )

    trade = Trade(

        symbol=symbol,

        side=side,

        price=price,

        quantity=quantity,

        pnl=(price - holding.average_price) * quantity
        if side == "SELL" and holding
        else 0,

        owner_id=user.id
    )

    db.add(trade)

    db.commit()

    db.refresh(trade)

    return {

        "message": "Trade executed",

        "trade": {

            "id": trade.id,

            "symbol": trade.symbol,

            "side": trade.side,

            "price": trade.price,

            "quantity": trade.quantity,

            "pnl": trade.pnl
        },

        "portfolio": {

            "balance": round(portfolio.balance, 2),

            "realized_pnl": round(portfolio.realized_pnl, 2)
        }
    }


@router.get("/all")
def get_trades(

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

    trades = db.query(Trade).filter(
        Trade.owner_id == user.id
    ).all()

    return trades