from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def home():
    return "LINE Bot is running!"

@app.route("/callback", methods=["POST"])
def callback():
    # Webhookリクエスト処理を実装予定
    return "Callback received!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)