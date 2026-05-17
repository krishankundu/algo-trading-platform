from fastapi import APIRouter
from fastapi import WebSocket
import requests
import asyncio

router = APIRouter()


@router.websocket("/ws/price/{symbol}")
async def websocket_price(
    websocket: WebSocket,
    symbol: str
):

    await websocket.accept()

    while True:

        try:

            response = requests.get(

                f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
            )

            data = response.json()

            await websocket.send_json({

                "symbol": symbol,

                "price": data["price"]
            })

            await asyncio.sleep(1)

        except Exception as e:

            print(e)

            break