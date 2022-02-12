from fastapi import FastAPI, Response, status

from app.api import deliveries, scrape, stocks, test

app = FastAPI(docs_url=None)


@app.get("/")
async def root():
    return Response(status_code=status.HTTP_200_OK)


app.include_router(deliveries.router)
app.include_router(stocks.router)
app.include_router(scrape.router)
app.include_router(test.router)
