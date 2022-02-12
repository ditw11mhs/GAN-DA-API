import json
import os
from itertools import accumulate

from dotenv import load_dotenv
from fastapi import FastAPI
from lxml import html
from requests import session
from requests_futures.sessions import FuturesSession

app = FastAPI()


def add_flatten_lists(the_lists):
    result = []
    for _list in the_lists:
        result += _list
    return result


@app.on_event("startup")
async def startup_event():
    load_dotenv()
    payload = {
        "userid": os.getenv("USER_DROPSHIP"),
        "password": os.getenv("PASSWORD_DROPSHIP"),
    }
    s = session()
    s.post("https://www.dropshipaja.com/page/login_code.php", data=payload)
    app.session = FuturesSession(session=s)
    app.delivery_id = json.load(open("result.json"))


@app.get("/")
async def root():
    return {"message": "Hello World "}


@app.get("/stocks/kaos")
async def check_stock_kaos():
    req_list = [
        app.session.get(
            "https://www.dropshipaja.com/kategoridesainonline.php?id=6&page=" + str(i)
        )
        for i in range(1, 10)
    ]

    tree_list = [html.fromstring(req.result().content) for req in req_list]

    stock_list = add_flatten_lists(
        [
            tree.cssselect(
                "h6[class='text-muted stock da-text-secondary-extra-dark mb-2']"
            )
            for tree in tree_list
        ]
    )
    product_name_list = add_flatten_lists(
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


@app.get("/deliveries/scrape/")
async def scrap_delivery_method():
    cek_ongkir = app.session.get(
        "https://www.dropshipaja.com/customer-track-ongkir.php"
    )
    tree_cek_ongkir = html.fromstring(cek_ongkir.result().content)
    list_province = [
        province.text for province in tree_cek_ongkir.xpath("//option[@value]")
    ]

    city_req_list = [
        app.session.post(
            "https://www.dropshipaja.com/customer-track-ongkir-kabupaten.php",
            data={"provinsi": province},
        )
        for province in list_province[1:35]
    ]
    city_html = [html.fromstring(city.result().content) for city in city_req_list]
    city_list = []
    for things in city_html:
        temp = []
        for element in things.xpath("//option[@value]")[1:]:
            temp.append(element.text)
        city_list.append(temp)

    city_flatten = add_flatten_lists(city_list)

    district_req_list = [
        app.session.post(
            "https://www.dropshipaja.com/customer-track-ongkir-kecamatan.php",
            data={"kabupaten": city},
        )
        for city in city_flatten
    ]
    district_html = [
        html.fromstring(district.result().content) for district in district_req_list
    ]
    district_id = []
    for things in district_html:
        temp = []
        for element in things.xpath("//option[@value]")[1:]:
            temp.append(element.attrib["value"])
        district_id.append(temp)

    district_list = []

    for city_district in district_id:
        temp_list = []
        for each in city_district:
            temp_list.append(each.split("|")[2].split("-")[0].title())
        district_list.append(temp_list)

    district_to_id = []
    for lis, id in zip(district_list, district_id):
        district_to_id.append(dict(zip(lis, id)))

    district_per_city = list(accumulate([len(lis) for lis in city_list]))

    city_to_district = []
    for i in range(len(district_per_city)):
        if i == 0:
            city_to_district.append(
                dict(
                    zip(
                        city_flatten[: district_per_city[i]],
                        district_to_id[: district_per_city[i]],
                    )
                )
            )
        else:
            city_to_district.append(
                dict(
                    zip(
                        city_flatten[district_per_city[i - 1] : district_per_city[i]],
                        district_to_id[district_per_city[i - 1] : district_per_city[i]],
                    )
                )
            )

    province_to_city = dict(zip(list_province[1:35], city_to_district))

    with open("result.json", "w") as fp:
        json.dump(province_to_city, fp)


@app.get("/deliveries/cost")
async def cost(province: str, city: str, district: str, weight: str):
    id = app.delivery_id[province][city][district]
    output = {}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    jnt_req = app.session.post(
        "https://www.dropshipaja.com/api-jnt/tarif.php",
        headers=headers,
        data={"berat": weight, "kecamatan": id},
    )

    jne_req = app.session.post(
        "https://www.dropshipaja.com/getdataongkir_jne_trackinguser.php",
        headers=headers,
        data={"id": id, "berat": weight, "kab": city, "kurir": "jne"},
    )

    sicepat_req = app.session.post(
        "https://www.dropshipaja.com/cek_ongkir.php",
        headers=headers,
        data={"berat": weight, "kab_id": city, "kurir": "sicepat", "subdistrict": id},
    )

    jnt_res = json.loads(jnt_req.result().json()["content"])[0]
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
