import json

from fastapi import FastAPI
from app.api import deliveries, stocks, scrape

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World "}


app.include_router(deliveries.router)
app.include_router(stocks.router)
app.include_router(scrape.router)
