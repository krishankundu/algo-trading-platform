from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from app.database.connection import SessionLocal

from app.database.models import User, Trade

from app.database.portfolio_model import Portfolio

from app.database.holding_model import Holding

from app.utils.jwt_handler import verify_token


router = APIRouter(
    prefix="/portfolio",
    tags=["Portfolio"]
)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.get("/me")
def get_portfolio(

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

    holdings = db.query(Holding).filter(
        Holding.user_id == user.id
    ).all()

    trades = db.query(Trade).filter(
        Trade.owner_id == user.id
    ).all()

    holdings_data = []

    for holding in holdings:

        holdings_data.append({

            "symbol": holding.symbol,

            "quantity": round(holding.quantity, 6),

            "average_price": round(holding.average_price, 2)
        })

    return {

        "user_id": user.id,

        "email": user.email,

        "balance": round(portfolio.balance, 2),

        "realized_pnl": round(portfolio.realized_pnl, 2),

        "total_trades": len(trades),

        "holdings": holdings_data
    }