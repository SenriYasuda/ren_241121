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
    # ファイルがリクエストに含まれていない場合
    if 'file' not in request.files:
        return jsonify({"error": "No file_mywrite"}), 400
    
    file = request.files['file']
    
    # ファイルが選択されていない場合
    if file.filename == '':
        return jsonify({"error": "No file_mywrite"}), 400
    
    # 有効なファイル形式の場合
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # アップロード先のフォルダがない場合は作成
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        
        # ファイルを保存
        file.save(filepath)

        # 画像は10分後に削除
        time.sleep(600)  # 10分
        os.remove(filepath)

        return jsonify({"message": "File uploaded successfully"}), 200
    
    # 無効なファイル形式の場合
    return jsonify({"error": "無効なファイル形式"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
