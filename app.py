from flask import Flask, request, jsonify, send_file, Response
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO
import os
import time
import glob
from apscheduler.schedulers.background import BackgroundScheduler

# Flaskアプリケーションの初期化
app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")  # 絶対パスに基づく設定
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Socket.IOの初期化
socketio = SocketIO(app)

# APSchedulerの初期化
scheduler = BackgroundScheduler()
scheduler.start()

# ファイル自動削除のスケジューリング
def schedule_file_deletion(file_path, delay=600):
    scheduler.add_job(func=os.remove, args=[file_path], trigger="date", run_date=time.time() + delay)

@app.route("/list-files", methods=["GET"])
def list_files():
    try:
        files = os.listdir(UPLOAD_FOLDER)
        return jsonify({"files": files})
    except FileNotFoundError:
        return jsonify({"error": "Upload folder not found"}), 404

@app.route('/get_image/<image_number>', methods=['GET'])
def get_image(image_number):
    search_pattern = os.path.join(UPLOAD_FOLDER, f"pic{image_number.zfill(3)}.jpg")
    matching_files = glob.glob(search_pattern)
    if matching_files:
        return send_file(matching_files[0], mimetype="image/jpeg")
    else:
        return "No picture or time up", 404

@app.route('/get_text_in/<text_number_in>', methods=['GET'])
def get_text_in(text_number_in):
    search_pattern = os.path.join(UPLOAD_FOLDER, f"text{text_number_in.zfill(3)}.txt")
    matching_files = glob.glob(search_pattern)
    if matching_files:
        file_path = matching_files[0]
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='shift_jis') as file:
                content = file.read()
        return Response(content, mimetype="text/plain")
    else:
        return "No text or time up", 404

@app.route("/upload", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Image and text files are required"}), 400

    # ファイルの保存
    image_file = request.files['file']
    image_filename = secure_filename(image_file.filename)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
    image_file.save(image_path)

    # 自動削除をスケジュール
    schedule_file_deletion(image_path)

    # クライアントに通知
    socketio.emit("file_ready", {"filename": image_filename})

    return jsonify({"message": "Files uploaded successfully", "image_path": image_path})

@socketio.on("connect")
def handle_connect():
    print("クライアントが接続されました。")

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
