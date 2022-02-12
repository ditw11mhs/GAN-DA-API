from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
from requests import session
from requests_futures.sessions import FuturesSession
from json import loads, load
import os


router = APIRouter(prefix="/deliveries", tags=["Deliveries"])


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
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")


@router.get("/cost")
@cache(expire=30)
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
    
    jnt_res = loads(jnt_req.result().json()["content"])[0]
    
    jne_res = jne_req.result().json()["price"]
    
    sicepat_res = sicepat_req.result().json()["rajaongkir"]["results"][0]["costs"]
    

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

    sicepat_dict = {}
    for sicepat_service in sicepat_res:
        service_name = sicepat_service["service"]
        sicepat_dict[service_name] = {
            "etd": sicepat_service["cost"][0]["etd"],
            "cost": str(sicepat_service["cost"][0]["value"]),
        }

    output["JNT"] = {"EZ": {"etd": "-", "cost": jnt_res["cost"]}}
    output["JNE"] = jne_dict
    output["Sicepat"] = sicepat_dict

    return output
