import sys

sys.path.append("../")

from fastapi import FastAPI
from bot import BotDropship, BotBank
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World "}


@app.get("/check_stock")
async def test():
    with BotDropship(teardown=True, debug=False) as b_drop:
        return b_drop.get_stock_routine()


@app.get("/delivery/method/{Province}/{City}/{District}/{Weight}")
async def get_delivery_method(Province, City, District, Weight):
    with BotDropship(teardown=True, debug=False) as b_drop:
        return b_drop.get_delivery_method_routine(
            {"Province": Province, "City": City, "District": District}, Weight
        )
