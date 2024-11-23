from flask import Flask, request, jsonify, send_file, send_from_directory
from werkzeug.utils import secure_filename
import os
import time
import threading

app = Flask(__name__)

# ファイルの保存先ディレクトリ
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")  # 絶対パスに変更
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
    # 画像名を生成 (例えば: pic001.jpg, pic002.jpg, ...)
    filename = f"pic{image_number.zfill(3)}.jpg"  # 数字をゼロ埋めしてフォーマット
    # 画像が存在するか確認
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        # 存在する場合、その画像を返す
        return send_file(file_path, mimetype="image/jpeg")  # mimetypeを変更
    else:
        # 画像が存在しない場合、エラーメッセージを返す
        return "No picture or time up", 404

@app.route('/upload_text', methods=['POST'])
def upload_text():
    global TEXT_DATA

    # JSON形式で文字列を受け取る
    data = request.get_json()
    key = data.get('key')  # 文字列のキー
    text = data.get('text')  # 保存する文字列

    if not key or not text:
        return jsonify({"error": "Key and text are required"}), 400

    # テキストデータを保存
    TEXT_DATA[key] = text
    return jsonify({"message": "Text data uploaded successfully", "key": key}), 200



# ファイルアップロード用エンドポイント
@app.route("/upload", methods=["POST"])
def upload_file():
    if 'file' not in request.files or 'text' not in request.form:
        return jsonify({"error": "File and text data required"}), 400

    # ファイル保存
    file = request.files['file']
    text = request.form['text']
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    print(f"ファイルパスは：{file_path}")
    # 自動削除のスレッド開始
    threading.Thread(target=auto_delete_file, args=(file_path,)).start()

    # 保存データの確認
    return jsonify({
        "message": "File uploaded successfully",
        "file_path": file_path,
        "text": text
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
