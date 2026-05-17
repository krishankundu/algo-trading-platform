from fastapi import FastAPI
import os
from fastapi.middleware.cors import CORSMiddleware
from app.routes.market import router as market_router
from app.routes.trade import router as trade_router
from app.routes.backtest import router as backtest_router
from app.routes.websocket import router as websocket_router
from app.routes.portfolio import router as portfolio_router
from app.routes.signal import router as signal_router
from app.database.holding_model import Holding
from app.database.portfolio_model import Portfolio
from app.database.connection import Base, engine

from app.routes.user import router as user_router
from app.routes.strategy import router as strategy_router

import app.database.models

Base.metadata.create_all(bind=engine)

app = FastAPI()

FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://localhost:5173"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        FRONTEND_URL,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(strategy_router)
app.include_router(market_router)
app.include_router(trade_router)
app.include_router(backtest_router)
app.include_router(websocket_router)
app.include_router(portfolio_router)
app.include_router(signal_router)

@app.get("/")
def home():

    return {
        "message": "Algo Trading API Running"
    }