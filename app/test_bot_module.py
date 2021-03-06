# import os
# from time import sleep
# from typing import Dict

# from dotenv import load_dotenv
# from seleniumrequests import Chrome
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.wait import WebDriverWait

# load_dotenv()

# import requests
# from lxml import html
# class BotBaseModel(Chrome):
#     def __init__(
#         self,
#         teardown=False,
#         debug=True,
#     ):

#         caps = DesiredCapabilities().CHROME
#         caps["pageLoadStrategy"] = "eager"
#         options = Options()
#         if not debug:
#             options.add_argument("--headless")
#         options.add_argument("--disable-dev_shm_usage")
#         # options.add_argument("--disable-gpu")
#         # options.add_argument("--no-sandbox")
#         options.add_argument("--disable-notifications")
#         options.add_argument(
#             "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0) Gecko/20100101 Firefox/39.0"
#         )
#         options.add_argument("window-size=1920x1080")
#         self.teardown = teardown
#         super(BotBaseModel, self).__init__(options=options, desired_capabilities=caps)

#     def __exit__(self, exc_type, exc_val, exc_tb):
#         if self.teardown:
#             self.quit()

#     def wait(self, time):
#         return WebDriverWait(self, time)

#     def wait_clickable(self, time, by, element):
#         return self.wait(time).until(EC.element_to_be_clickable((by, element)))


# class BotDropship(BotBaseModel):
#     def login(self):

#         self.get("https://dropshipaja.com/login.php")
#         # print("Login")
#         self.wait_clickable(10, By.NAME, "userid").send_keys(os.getenv("USER"))
#         self.wait_clickable(10, By.NAME, "password").send_keys(os.getenv("PASSWORD"))
#         self.wait_clickable(10, By.CSS_SELECTOR, "[type='submit']").click()

#     def close_ad(self):
#         self.wait_clickable(10, By.XPATH, "//button[@class='close n z']").click()

#     def go_to_apparel_page(self):
#         # print("Go to Apparel Page")
#         self.wait_clickable(
#             10,
#             By.CSS_SELECTOR,
#             "div[class='d-flex justify-content-start scroll-da'] a:nth-child(2)",
#         ).click()

#     def get_stock(self):
#         self.wait(10).until(
#             EC.presence_of_element_located(
#                 (By.CSS_SELECTOR, "div[class='same-height-row row products']")
#             )
#         )
#         # print("Getting Stock")
#         product_name = self.get_product_name_list()
#         product_stock = self.get_product_stock_list()
#         stock_dict = dict(zip(product_name, product_stock))
#         print(stock_dict)
#         return stock_dict

#     def get_product_stock_list(self):
#         return [
#             int(element.text.split(" ")[1])
#             for element in self.find_elements(
#                 By.CSS_SELECTOR,
#                 "h6[class='text-muted stock da-text-secondary-extra-dark mb-2']",
#             )
#         ]

#     def get_product_name_list(self):
#         return [
#             element.text
#             for element in self.find_elements(
#                 By.CSS_SELECTOR, "h5[class='text-left text-justify prdktitlenp']"
#             )
#         ]
# # Can be faster
#     def get_stock_routine(self):
        
        
#         payload = {'userid':'aditya.wardianto11@gmail.com','password':'Laliteraturaesfuego11'}
        
#         session = requests.Session()
#         idk2=session.post('https://www.dropshipaja.com/page/login_code.php',data=payload)
#         idk = session.get("https://www.dropshipaja.com/kategoridesainonline.php?id=6")
#         tree = html.fromstring(idk.content)
#         test = tree.cssselect("h6[class='text-muted stock da-text-secondary-extra-dark mb-2']")
#         test_2 = tree.cssselect("h5[class='text-left text-justify prdktitlenp']")
#         return dict(zip([i.text for i in test_2],[i.text for i in test]))
    
# # Can be faster
#     def get_delivery_method(self, address, weight):

#         # print("Go to Delivery Method Page")
#         self.wait_clickable(10, By.XPATH, "//li[contains(.,'Cek Ongkir')]").click()

#         # print("Select Province")
#         self.wait_clickable(10, By.XPATH, "//b[1]").click()
#         self.wait_clickable(10, By.XPATH, f"//li[.='{address['Province']}']").click()

#         # print("Select City")
#         self.wait_clickable(10, By.ID, "kabupaten").click()
#         self.wait_clickable(10, By.XPATH, f"//option[.='{address['City']}']").click()

#         # print("Select District")
#         self.wait_clickable(10, By.ID, "kecamatan").click()
#         self.wait_clickable(
#             10, By.XPATH, f"//option[.='{address['District']}']"
#         ).click()

#         # print("Select Weight")
#         weight_form = self.wait_clickable(10, By.ID, "berat")
#         weight_form.send_keys(Keys.CONTROL, "a")
#         weight_form.send_keys(Keys.BACKSPACE)
#         weight_form.send_keys(weight)

#         # print("Submit")
#         self.wait_clickable(10, By.XPATH, "//button[@class='btn btn-primary']").click()

#         sleep(2)
#         table = self.wait(10).until(
#             EC.presence_of_element_located(
#                 (By.XPATH, "//tbody[@class='hasil-desktop']")
#             )
#         )

#         out = []

#         for row in table.find_elements(By.XPATH, "./tr"):
#             string = " "
#             for td in row.find_elements(By.XPATH, "./td"):
#                 string = string + td.text + " "
#             out.append(string)
#         print(out)
#         return out

#     def get_delivery_method_routine(self, address, weight):
#         self.login()
#         return self.get_delivery_method(address, weight)


# class BotBank(BotBaseModel):
#     def logout(self):
#         self.wait_clickable(10, By.ID, "nav-logout").click()
#         self.wait_clickable(10, By.ID, "btnCancelReg").click()

#     def login(self):
#         self.get("https://ibank.bankmandiri.co.id/retail3/loginfo/loginRequest")

#         self.wait_clickable(
#             10,
#             By.ID,
#             "userid_sebenarnya",
#         ).send_keys(os.getenv("USER_BANK"))

#         self.wait_clickable(
#             10,
#             By.ID,
#             "pwd_sebenarnya",
#         ).send_keys(os.getenv("PASSWORD_BANK"))

#         self.wait_clickable(
#             10,
#             By.ID,
#             "btnSubmit",
#         ).click()

#     def check_transaction(self):
#         self.login()

#         self.wait_clickable(
#             10, By.XPATH, "//div[@class='acc-group']//div[@class='acc-left']"
#         ).click()

#         # self.logout()
