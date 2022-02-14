from os import getenv

from dotenv import load_dotenv
from fastapi import FastAPI, Response, status

from app.api import deliveries, scrape, stocks, test

load_dotenv()

app = FastAPI()


@app.get("/")
async def root():
    return Response(status_code=status.HTTP_200_OK)


app.include_router(deliveries.router)
app.include_router(stocks.router)
app.include_router(test.router)
if getenv("DEPLOY") == "False":
    app.include_router(scrape.router)
