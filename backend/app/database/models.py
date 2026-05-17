from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from app.database.portfolio_model import Portfolio
from app.database.connection import Base


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String, unique=True, index=True)

    email = Column(String, unique=True, index=True)

    password = Column(String)

    strategies = relationship(
        "Strategy",
        back_populates="owner"
    )


class Strategy(Base):

    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String)

    symbol = Column(String)

    timeframe = Column(String)

    strategy_type = Column(String)

    buy_condition = Column(String)

    sell_condition = Column(String)

    trigger_enabled = Column(Boolean, default=False)

    order_quantity = Column(Float, default=1)

    last_signal = Column(String, default="WAIT")

    owner_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    owner = relationship(
        "User",
        back_populates="strategies"
    )

class Trade(Base):

    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)

    symbol = Column(String)

    side = Column(String)

    price = Column(Float)

    quantity = Column(Float)

    pnl = Column(Float, default=0)

    owner_id = Column(Integer, ForeignKey("users.id"))