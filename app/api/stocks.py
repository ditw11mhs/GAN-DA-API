import os

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
from lxml import html
from requests import session
from requests_futures.sessions import FuturesSession
from ujson import load

from app.utils import *

router = APIRouter(prefix="/stocks", tags=["Stocks"])


@router.on_event("startup")
async def startup_stocks():
    if os.getenv("DEPLOY") is "False":
        load_dotenv()

    payload = {
        "userid": os.getenv("USER_DROPSHIP"),
        "password": os.getenv("PASSWORD_DROPSHIP"),
    }
    s = session()
    s.post("https://www.dropshipaja.com/page/login_code.php", data=payload)
    router.session = FuturesSession(session=s)
    router.delivery_id = load(open(os.path.join("app", "data", "route_id.json")))
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")


@router.get("/kaos")
@cache(expire=600)
async def check_stock_kaos():
    req_list = [
        router.session.get(
            "https://www.dropshipaja.com/kategoridesainonline.php?id=6&page=" + str(i)
        )
        for i in range(1, 10)
    ]

    tree_list = [html.fromstring(req.result().content) for req in req_list]
    stock_list = flat(
        [
            tree.cssselect(
                "h6[class='text-muted stock da-text-secondary-extra-dark mb-2']"
            )
            for tree in tree_list
        ]
    )
    product_name_list = flat(
        [
            tree.cssselect("h5[class='text-left text-justify prdktitlenp']")
            for tree in tree_list
        ]
    )

    return dict(
        zip(
            [
                i.text.replace(
                    "\n                              CUSTOM KAOS ", ""
                ).replace("                            ", "")
                for i in product_name_list
            ],
            [i.text.replace(" ", "").replace("stock", "") for i in stock_list],
        )
    )
