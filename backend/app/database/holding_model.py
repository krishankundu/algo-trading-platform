from sqlalchemy import Column, Integer, Float, String, ForeignKey

from app.database.connection import Base


class Holding(Base):

    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    symbol = Column(String, index=True)

    quantity = Column(Float, default=0)

    average_price = Column(Float, default=0)