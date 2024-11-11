To set up an automated **`git pull`** on your server whenever you push to the main branch on GitHub, you can use GitHub’s **webhooks** combined with a **post-receive Git hook** on your server. This will trigger the `git pull` operation automatically on your server after any new commits are pushed to the main branch.

Here’s how to set it up:

### Step 1: Set Up a GitHub Webhook

1. Go to your repository on **GitHub**.
2. Navigate to **Settings** > **Webhooks** > **Add webhook**.
3. Under **Payload URL**, enter the URL of your server endpoint that will receive the webhook (for example, `http://yourserver.com/git-webhook`).
4. Set **Content type** to `application/json`.
5. In the **Secret** field, you can add a unique key that will secure your webhook (optional but recommended).
6. Under **Which events would you like to trigger this webhook?**, select **Just the push event**.
7. Click **Add webhook**.  

### Step 2: Create a Server Endpoint to Listen for the Webhook

Set up a small script on your server to listen for the GitHub webhook. Here’s an example using **Python** and **Flask** to listen for incoming webhook requests and trigger the `git pull` command.

1. Install **Flask** on your server if you haven’t already:

   ```bash
   pip install Flask
   ```
2. Create a `git-webhook.py` script:

   ```python
   from flask import Flask, request
   import os
   import hmac
   import hashlib

   app = Flask(__name__)
   SECRET_TOKEN = 'your_secret_here'  # Use the same secret you used in GitHub

   def verify_signature(data, signature):
       mac = hmac.new(SECRET_TOKEN.encode(), data, hashlib.sha256).hexdigest()
       return hmac.compare_digest(f'sha256={mac}', signature)

   @app.route('/git-webhook', methods=['POST'])
   def git_webhook():
       signature = request.headers.get('X-Hub-Signature-256')
       if SECRET_TOKEN and not verify_signature(request.data, signature):
           return 'Unauthorized', 401

       # Get the JSON payload
       payload = request.json
       if payload.get('ref') == 'refs/heads/main':  # Trigger only on main branch push
           # Run git pull
           os.system('cd /path/to/your/repo && git pull origin main')
           return 'Pulled successfully', 200
       return 'Not a main branch push', 400

   if __name__ == '__main__':
       app.run(host='0.0.0.0', port=5000)
   ```
3. Replace `/path/to/your/repo` with the directory path to your local repository on the server.
4. Replace `your_secret_here` with the secret you set on the GitHub webhook.
5. Run this script on your server:

   ```bash
   python git-webhook.py
   ```

   You may want to run this as a background service (e.g., with `nohup` or `systemd`) so that it’s always listening for incoming requests.

### Step 3: Test the Webhook

1. Push a commit to the **main** branch on GitHub.
2. GitHub should send a POST request to your server’s `/git-webhook` endpoint, triggering the `git pull` command if the push was to the main branch.
3. Check your server’s logs to confirm that the `git pull` was successful.

This setup will pull new changes on your server every time you push to the main branch on GitHub.

---

https://mydomain.com:9000/postreceive

Certificate Path: /etc/letsencrypt/live/dev2.monitor.eco.br/fullchain.pem
Private Key Path: /etc/letsencrypt/live/dev2.monitor.eco.br/privkey.pem

ngrok

[Setup - ngrok](https://dashboard.ngrok.com/get-started/setup/windows)

ngrok config add-authtoken XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

ngrok http http://localhost:8080

ngrok http --url baz.ngrok.dev 8080                           # port 8080 available at baz.ngrok.dev
