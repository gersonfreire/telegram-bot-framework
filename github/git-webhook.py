from flask import Flask, request
import os
import hmac
import hashlib

app = Flask(__name__)
SECRET_TOKEN = 'your_secret_here'  # Use the same secret you used in GitHub

def verify_signature(data, signature):
    mac = hmac.new(SECRET_TOKEN.encode(), data, hashlib.sha256).hexdigest()
    return hmac.compare_digest(f'sha256={mac}', signature)

@app.route('/git-webhook', methods=['POST','GET'])
def git_webhook():
    try:
        signature = request.headers.get('X-Hub-Signature-256')
        if SECRET_TOKEN and not verify_signature(request.data, signature):
            # return 'Unauthorized', 401
            pass

        # Get the JSON payload
        payload = request.json
        if payload.get('ref') == 'refs/heads/main':  # Trigger only on main branch push
            # Run git pull
            # os.system('cd /path/to/your/repo && git pull origin main')
            os.system('git pull origin main')
            return 'Pulled successfully', 200
        return 'Not a main branch push', 400
    except Exception as e:
        return f'Error: {str(e)}', 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)