from bot import BotBank, BotDropship
import time

with BotDropship(teardown=False, debug=True) as bot:
    start = time.time()
    bot.get_delivery_method(
        {
            "Province": "Jawa Timur",
            "City": "Surabaya",
            "District": "Simokerto",
            "Address": "Jl. Raya Klaten",
        },
        2,
    )
    end = time.time()
    print(end - start)
