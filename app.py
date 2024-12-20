from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO
import os
import time
import threading
import glob
import eventlet

eventlet.monkey_patch()

app = Flask(__name__)

# ファイルの保存先ディレクトリ
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

socketio = SocketIO(app)

# 自動削除の設定（10分後に削除）
def auto_delete_file(file_path, delay=600):
    time.sleep(delay)
    if os.path.exists(file_path):
        os.remove(file_path)

@app.route("/upload", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Image and text files are required"}), 400

    image_file = request.files['file']
    image_filename = secure_filename(image_file.filename)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
    image_file.save(image_path)

    print(f"画像ファイルパス: {image_path}")

    # 自動削除のスレッド開始
    threading.Thread(target=auto_delete_file, args=(image_path,)).start()

    # クライアントに通知
    socketio.emit("file_ready", {"filename": image_filename})

    return jsonify({
        "message": "Files uploaded successfully",
        "image_path": image_path,
    })

@socketio.on("connect")
def handle_connect():
    print("クライアントが接続されました。")

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
