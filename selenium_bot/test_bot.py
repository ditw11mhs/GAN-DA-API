from bot import BotBank, BotDropship
import time

with BotBank(teardown=False, debug=True) as bot:
    # start = time.time()
    bot.check_transaction()
    # bot.get_stock_routine()
    # bot.get_delivery_method(
    #     {
    #         "Province": "Jawa Timur",
    #         "City": "Surabaya",
    #         "District": "Simokerto",
    #         "Address": "Jl. Raya Klaten",
    #     },
    #     2,
    # )
    # end = time.time()
    # print(end - start)
