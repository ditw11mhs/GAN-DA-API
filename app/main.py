import json
from itertools import accumulate
from app.utils import *
from lxml import html
from requests import session
from app.api import deliveries, stocks

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World "}


app.include_router(deliveries.router)
app.include_router(stocks.router)


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

    city_flatten = flat(city_list)

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
