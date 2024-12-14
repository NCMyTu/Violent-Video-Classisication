import os
import cv2
import numpy as np
import requests
from io import BytesIO
from flask import Flask, render_template, request, redirect, url_for, jsonify

UPLOAD_FOLDER = './static/uploads'
BATCH_SIZE = 32

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['video']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = file.filename
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    return jsonify({
        "message": "File uploaded successfully!",
        "video_url": url_for('static', filename=f'uploads/{filename}')
    })

@app.route('/cctv_infer', methods=['POST'])
def cctv_infer():
    result = "detected (x, y), conf: 0.95"
    return result


if __name__ == '__main__':
    app.run(debug=True)