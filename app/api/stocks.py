import os

from diskcache import Cache
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from lxml import html
from requests import session
from requests_futures.sessions import FuturesSession
from ujson import load

from app.utils import *

router = APIRouter(prefix="/stocks", tags=["Stocks"])


@router.on_event("startup")
async def startup_stocks():
    if os.getenv("DEPLOY") == "False":
        load_dotenv()

    payload = {
        "userid": os.getenv("USER_DROPSHIP"),
        "password": os.getenv("PASSWORD_DROPSHIP"),
    }
    s = session()
    s.post("https://www.dropshipaja.com/page/login_code.php", data=payload)
    router.session = FuturesSession(session=s)
    router.delivery_id = load(open(os.path.join("app", "data", "route_id.json")))
    router.cache = Cache()


@router.get("/kaos")
async def check_stock_kaos():
    router.cache.expire()
    if "stock_kaos" in list(router.cache):
        return router.cache.get("stock_kaos")
    else:
        req_list = [
            router.session.get(
                "https://www.dropshipaja.com/kategoridesainonline.php?id=6&page="
                + str(i)
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
        out = dict(
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
        router.cache.set("stock_kaos", out, expire=600, tag="stock")
        return out
