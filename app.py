from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import time
import threading

app = Flask(__name__)

# ファイルの保存先ディレクトリ
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")  # 絶対パスに変更
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# メモリ上で文字列データを管理
text_data = {}

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
    filename = f"pic{image_number.zfill(3)}.jpg"  # 数字をゼロ埋めしてフォーマット
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, mimetype="image/jpeg")  # mimetypeを変更
    else:
        return "No picture or time up", 404


# 文字列の取得エンドポイント
@app.route('/get_text/<key>', methods=['GET'])
def get_text(key):
    # 指定されたキーに対応する文字列を取得
    text = text_data.get(key)
    if text is None:
        return jsonify({"error": "Key not found"}), 404
    return jsonify({"key": key, "text": text}), 200


# ファイルアップロード用エンドポイント
@app.route("/upload", methods=["POST"])
def upload_file():
    # 必須フィールドのチェック
    if 'file' not in request.files or 'key' not in request.form or 'text' not in request.form:
        return jsonify({"error": "File, key, and text data required"}), 400

    # ファイル保存
    file = request.files['file']
    key = request.form['key']
    text = request.form['text']

    # キーの重複チェック
    if key in text_data:
        return jsonify({"error": "Key already exists"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # 文字列を保存
    text_data[key] = text

    # 自動削除のスレッド開始
    threading.Thread(target=auto_delete_file, args=(file_path,)).start()

    return jsonify({
        "message": "File and text uploaded successfully",
        "key": key,
        "text": text,
        "file_path": file_path
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
