from flask import Flask, request, jsonify
import os
import time
from werkzeug.utils import secure_filename

app = Flask(__name__)

# アップロード先のフォルダ
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# アップロードファイルの拡張子を確認
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ゲーム結果を受け取るAPI
@app.route('/upload_result', methods=['POST'])
def upload_result():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        # 画像は5分後に削除
        time.sleep(300)
        os.remove(filepath)
        return jsonify({"message": "File uploaded successfully"}), 200
    return jsonify({"error": "Invalid file format"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
