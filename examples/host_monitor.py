import os
import time
from tlgfwk import TlgBotFwk

def ping_host(ip_address):
    response = os.system(f"ping -c 1 {ip_address}")
    if response == 0:
        print(f"{ip_address} is up!")
    else:
        print(f"{ip_address} is down!")

class HostMonitorBot(TlgBotFwk):
    def __init__(self, ip_address):
        super().__init__()
        self.ip_address = ip_address

    def job(self):
        self.ping_host(self.ip_address)

    def ping_host(self, ip_address):
        response = os.system(f"ping -c 1 {ip_address}")
        if response == 0:
            print(f"{ip_address} is up!")
        else:
            print(f"{ip_address} is down!")

# Create an instance of the bot
bot = HostMonitorBot("8.8.8.8")

# Schedule the job every 10 minutes using the bot's scheduling method
bot.schedule.every(10).minutes.do(bot.job)

# Start the bot's main loop
bot.run()

# Schedule the job every 10 minutes
# schedule.every(10).minutes.do(job)

# while True:
#     schedule.run_pending()
#     time.sleep(1)