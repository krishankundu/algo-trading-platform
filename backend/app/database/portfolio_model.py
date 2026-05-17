from sqlalchemy import Column, Integer, Float, ForeignKey

from app.database.connection import Base


class Portfolio(Base):

    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    balance = Column(Float, default=10000)

    realized_pnl = Column(Float, default=0)