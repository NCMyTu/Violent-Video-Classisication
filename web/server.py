import os
import cv2
import numpy as np
import base64
from flask import Flask, render_template, request, url_for, jsonify, Response

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

@app.route('/sendURL', methods=['POST'])
def send_cctv_url():
    count = 0
    data = request.get_json()
    cctv_url = data.get('cctvURL')
    print(cctv_url)
    cap = cv2.VideoCapture(cctv_url)
    if not cap.isOpened():
        return jsonify(message="Unable to open stream"), 400

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        processed_data = process_frame(frame)
        print(count)
        count += 1

        return jsonify(processed_data)

    cap.release()
    return jsonify(message="Stream processed successfully")

def process_frame(frame):
    return {
        'objects_detected': f"{frame.shape}"
    }

if __name__ == '__main__':
    app.run(debug=True)