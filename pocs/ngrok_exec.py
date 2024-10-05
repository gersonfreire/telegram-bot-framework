import subprocess
import json, os
import time
import requests

def start_ngrok():
    # Start ngrok process
    # ngrok\ngrok.exe http 80
    ngrok_path = os.path.join(os.path.dirname(__file__), '..', 'ngrok', 'ngrok.exe')
    ngrok = subprocess.Popen([ngrok_path, 'http', '5000'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(5)  # Wait for ngrok to initialize

    # Get the ngrok tunnels
    response = requests.get('http://localhost:4040/api/tunnels')
    if response.status_code == 200:
        tunnels = response.json()['tunnels']
        for tunnel in tunnels:
            if tunnel['proto'] == 'https':
                return tunnel['public_url']
    return None

if __name__ == "__main__":
    url = start_ngrok()
    if url:
        print(f"Ngrok URL: {url}")
    else:
        print("Failed to get ngrok URL")