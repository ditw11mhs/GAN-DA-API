from bot_module import BotBank, BotDropship
import time

with BotDropship(teardown=False, debug=True) as bot:
    # start = time.time()
    # bot.check_transaction()
    # bot.get_stock_routine()
    bot.get_delivery_method_routine(
        {
            "Province": "Jawa Timur",
            "City": "Surabaya",
            "District": "Simokerto",
            "Address": "Jl. Raya Klaten",
        },
        2,
    )
    # bot.login()
    # end = time.time()
    # print(end - start)
