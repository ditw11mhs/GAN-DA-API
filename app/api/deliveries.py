import os
from json import load, loads

from diskcache import Cache
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from requests import session
from requests_futures.sessions import FuturesSession

router = APIRouter(prefix="/deliveries", tags=["Deliveries"])


@router.on_event("startup")
async def startup_deliveries():
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
    router.cache = Cache()


@router.get("/cost")
async def cost(province: str, city: str, district: str, weight: str):
    try:
        id = router.delivery_id[province][city][district]
    except:
        HTTPException(status_code=404, detail="Not Found")

    router.cache.expire()
    if f"{province}_{city}_{district}_{weight}" in list(router.cache):
        return router.cache.get(
            f"{province}_{city}_{district}_{weight}",
            tag=f"delivery_{province}_{city}_{district}",
        )
    else:
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
            data={
                "berat": weight,
                "kab_id": city,
                "kurir": "sicepat",
                "subdistrict": id,
            },
        )

        jnt_parse(output, jnt_req)
        jne_parse(output, jne_req)
        sicepat_parse(output, sicepat_req)

        router.cache.set(
            f"{province}_{city}_{district}_{weight}",
            output,
            expire=3600,
            tag=f"delivery_{province}_{city}_{district}",
        )

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
