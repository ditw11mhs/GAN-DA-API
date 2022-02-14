import random
from os import getenv, path

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from requests import session
from requests_futures.sessions import FuturesSession
from ujson import dump, load, loads

router = APIRouter(prefix="/tests", tags=["Test"])


@router.on_event("startup")
async def startup_deliveries():
    if getenv("DEPLOY") == "False":
        load_dotenv()
    payload = {
        "userid": getenv("USER_DROPSHIP"),
        "password": getenv("PASSWORD_DROPSHIP"),
    }
    s = session()
    s.post("https://www.dropshipaja.com/page/login_code.php", data=payload)
    router.session = FuturesSession(session=s)
    router.delivery_id = load(open(path.join("app", "data", "route_id.json")))
    router.del_list = list(router.delivery_id.items())


@router.get("/random")
async def random_things():
    province, city = random.choice(router.del_list)
    city, district = random.choice(list(city.items()))
    district, _ = random.choice(list(district.items()))
    return await cost(
        province, city, district, weight=str(random.randrange(200, 2000, 200))
    )


@router.get("/route_id_json")
async def test_json():
    task = []

    for province in router.delivery_id.keys():
        out_dict = {}
        out_dict[province] = {}
        for city in router.delivery_id[province].keys():
            out_dict[province][city] = {}
            for district in router.delivery_id[province][city]:
                out_dict[province][city][district] = {}
                task.append(
                    router.session.get(
                        getenv("DEPLOYED_ROOT_API")
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
        with open(path.join("app", "test", province + ".json"), "w") as fp:
            dump(out_dict, fp)


async def cost(province: str, city: str, district: str, weight: str):
    try:
        id = router.delivery_id[province][city][district]
    except:
        HTTPException(status_code=404, detail="Not Found")

    output = {}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    jnt_req = router.session.post(
        "https://www.dropshipaja.com/api-jnt/tarif.php",
        headers=headers,
        data={"berat": weight, "kecamatan": id},
    )
    jne_req = router.session.post(
        "https://www.dropshipaja.com/getdataongkir_jne_trackinguser.php",
        headers=headers,
        data={"id": id, "berat": weight, "kab": city, "kurir": "jne"},
    )

    sicepat_req = router.session.post(
        "https://www.dropshipaja.com/cek_ongkir.php",
        headers=headers,
        data={"berat": weight, "kab_id": city, "kurir": "sicepat", "subdistrict": id},
    )

    jnt_parse(output, jnt_req)
    jne_parse(output, jne_req)
    sicepat_parse(output, sicepat_req)

    return output


def jnt_parse(output, jnt_req):
    res = jnt_req.result().json()
    if "content" in res:
        jnt_res = loads(res["content"])[0]
        output["JNT"] = {"EZ": {"etd": "-", "cost": jnt_res["cost"]}}


def sicepat_parse(output, sicepat_req):
    res = sicepat_req.result().json()["rajaongkir"]
    if "results" in res:
        sicepat_res = res["results"][0]["costs"]
        sicepat_dict = {}
        for sicepat_service in sicepat_res:
            service_name = sicepat_service["service"]
            sicepat_dict[service_name] = {
                "etd": sicepat_service["cost"][0]["etd"],
                "cost": str(sicepat_service["cost"][0]["value"]),
            }
        output["Sicepat"] = sicepat_dict


def jne_parse(output, jne_req):
    res = jne_req.result().json()
    if "price" in res:
        jne_res = res["price"]
        jne_dict = {}
        for jne_service in jne_res:
            service_name = jne_service["service_display"]
            if "JTR" in service_name:
                continue

            if jne_service["etd_from"] != jne_service["etd_thru"]:
                if None not in (jne_service["etd_from"], jne_service["etd_thru"]):
                    to_etd = jne_service["etd_from"] + "-" + jne_service["etd_thru"]
                else:
                    to_etd = "-"
            else:
                to_etd = jne_service["etd_from"]

            jne_dict[service_name] = {
                "etd": to_etd,
                "cost": jne_service["price"],
            }
        output["JNE"] = jne_dict
