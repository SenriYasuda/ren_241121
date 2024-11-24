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
    # 画像名を生成
    filename = f"pic{image_number.zfill(3)}.jpg"  # 数字をゼロ埋めしてフォーマット
    # 画像が存在するか確認
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        # 存在する場合、その画像を返す
        return send_file(file_path, mimetype="image/jpeg")  # mimetypeを変更
    else:
        # 画像が存在しない場合、エラーメッセージを返す
        return "No picture or time up", 404

# ファイルアップロード用エンドポイント
@app.route("/upload", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Image and text files are required"}), 400

    # 画像ファイル保存
    image_file = request.files['file']
    image_filename = secure_filename(image_file.filename)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
    image_file.save(image_path)

    # テキストファイル保存
    #text_file = request.files['text_file']
    #text_filename = secure_filename(text_file.filename)
    #text_path = os.path.join(app.config['UPLOAD_FOLDER'], text_filename)
    #text_file.save(text_path)

    print(f"画像ファイルパス: {image_path}")
    #print(f"テキストファイルパス: {text_path}")

    # 自動削除のスレッド開始
    threading.Thread(target=auto_delete_file, args=(image_path,)).start()
    #threading.Thread(target=auto_delete_file, args=(text_path,)).start()

    # 保存データの確認
    return jsonify({
        "message": "Files uploaded successfully",
        "image_path": image_path,
        #"text_path": text_path,
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
