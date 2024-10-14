import os
import time
import schedule

def ping_host(ip_address):
    response = os.system(f"ping -c 1 {ip_address}")
    if response == 0:
        print(f"{ip_address} is up!")
    else:
        print(f"{ip_address} is down!")

def job():
    ping_host("8.8.8.8")

# Schedule the job every 10 minutes
schedule.every(10).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)