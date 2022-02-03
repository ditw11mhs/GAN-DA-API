import sys

sys.path.append("..")
from fastapi import FastAPI
from selenium_bot.bot import BotDropship, BotBank
import json
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World "}


@app.get("/test")
async def test():
    with BotDropship(teardown=True, debug=False) as b_drop:
        return JSONResponse(b_drop.get_stock_routine())
    

