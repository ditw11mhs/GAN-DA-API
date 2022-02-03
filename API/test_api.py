import sys

sys.path.append("..")
import json

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from selenium_bot.bot import BotBank, BotDropship

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World "}


@app.get("/test")
async def test():
    with BotDropship(teardown=True, debug=False) as b_drop:
        return JSONResponse(b_drop.get_stock_routine())
