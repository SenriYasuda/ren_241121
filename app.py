from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
from flask import Flask
from flask_socketio import SocketIO
import os
import time
import threading
import glob
import eventlet

eventlet.monkey_patch()
app = Flask(__name__)

# ファイルの保存先ディレクトリ
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")  # 絶対パスに変更
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

socketio = SocketIO(app)

# 自動削除の設定（10分後に削除）
def auto_delete_file(file_path, delay=600):
    time.sleep(delay)
    if os.path.exists(file_path):
        os.remove(file_path)

@app.route("/list-files", methods=["GET"])
def list_files():
    try:
        files = os.listdir(UPLOAD_FOLDER)
        return jsonify({"files": files})
    except FileNotFoundError:
        return jsonify({"error": "Upload folder not found"}), 404

# 画像の取得エンドポイント
@app.route('/get_image/<image_number>', methods=['GET'])
def get_image(image_number):
    search_pattern = os.path.join(UPLOAD_FOLDER, f"pic{image_number.zfill(3)}*")
    matching_files = glob.glob(search_pattern)
    if matching_files:
        return send_file(matching_files[0], mimetype="image/jpeg")
    else:
        return "No picture or time up", 404


# ファイルアップロード用エンドポイント
@app.route("/upload", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Image and text files are required"}), 400

    # 画像ファイル保存
    image_file = request.files['file']
    image_filename = secure_filename(image_file.filename)  # ファイル名を安全に処理
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
    image_file.save(image_path)

    print(f"画像ファイルパス: {image_path}")

    # クライアントに通知
    socketio.emit("file_ready", {"filename": image_filename})

    # 自動削除のスレッド開始
    threading.Thread(target=auto_delete_file, args=(image_path,)).start()

    return jsonify({
        "message": "Files uploaded successfully",
        "image_path": image_path,
    })

# クライアント通知用エンドポイント（デバッグ用）
@socketio.on("connect")
def handle_connect():
    print("クライアントが接続されました。")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
