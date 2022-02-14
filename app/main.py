from dotenv import load_dotenv
from os import getenv
from fastapi import FastAPI, Response, status
from app.api import deliveries, stocks, scrape, test

load_dotenv()

app = FastAPI()


@app.get("/")
async def root():
    return Response(status_code=status.HTTP_200_OK)


app.include_router(deliveries.router)
app.include_router(stocks.router)
if getenv("DEPLOY") == "False":
    app.include_router(test.router)
    app.include_router(scrape.router)
