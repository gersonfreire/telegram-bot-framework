from flask import Flask, request, render_template_string

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Telegram Web App</title>
        </head>
        <body>
            <h1>Enter your name</h1>
            <form action="/submit" method="post">
                <label for="name">Your name:</label>
                <input type="text" id="name" name="name">
                <input type="submit" value="Submit">
            </form>
        </body>
        </html>
    ''')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    # return f'<script>window.Telegram.WebApp.sendData("{name}");</script>'
    return f'''
    <script>
        if (window.Telegram.WebApp) {
            window.Telegram.WebApp.sendData("{name}");
            console.log("Data sent: {name}");
        } else {
            console.error("Telegram Web App is not initialized.");
        }
    </script>
    '''

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')