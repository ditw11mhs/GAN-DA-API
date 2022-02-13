from ujson import load, dump
import random
from dotenv import load_dotenv
from fastapi import APIRouter
from requests import session
from requests_futures.sessions import FuturesSession
import os


router = APIRouter(prefix="/test", tags=["Test"])


@router.on_event("startup")
async def startup_deliveries():
    if os.getenv("DEPLOY") is None:
        load_dotenv()
    payload = {
        "userid": os.getenv("USER_DROPSHIP"),
        "password": os.getenv("PASSWORD_DROPSHIP"),
    }
    s = session()
    s.post("https://www.dropshipaja.com/page/login_code.php", data=payload)
    router.session = FuturesSession(session=s)
    router.delivery_id = load(open(os.path.join("app", "data", "route_id.json")))
    router.del_list = list(router.delivery_id.items())


@router.get("/random")
async def random_things():
    province, city = random.choice(router.del_list)
    city, district = random.choice(list(city.items()))
    district, _ = random.choice(list(district.items()))
    return (
        os.getenv("DELOYED_ROOT_API")
        + "/deliveries/cost?province="
        + province.replace(" ", "%20")
        + "&city="
        + city.replace(" ", "%20")
        + "&district="
        + district.replace(" ", "%20")
        + "&weight="
        + str(random.randrange(200, 2000, 200))
    )


@router.get("/route_id_json")
async def test_json():
    task = []
    out_dict = {}
    for province in router.delivery_id.keys():
        out_dict[province] = {}
        for city in router.delivery_id[province].keys():
            out_dict[province][city] = {}
            for district in router.delivery_id[province][city]:
                out_dict[province][city][district] = {}
                task.append(
                    router.session.get(
                        os.getenv("DEPLOYED_ROOT_API")
                        + "/deliveries/cost?province="
                        + province.replace(" ", "%20")
                        + "&city="
                        + city.replace(" ", "%20")
                        + "&district="
                        + district.replace(" ", "%20")
                        + "&weight="
                        + str(random.randrange(200, 2000, 200))
                    )
                )
        count = 0
        for city in router.delivery_id[province].keys():
            for district in router.delivery_id[province][city]:
                out_dict[province][city][district] = task[count].result().status_code
                count += 1
        with open(os.path.join("app", "test", province + ".json"), "w") as fp:
            dump(out_dict, fp)
