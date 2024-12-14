import os
import cv2
import numpy as np
import requests
from io import BytesIO
from flask import Flask, render_template, request, redirect, url_for, jsonify

BATCH_SIZE = 32

app = Flask(__name__)
UPLOAD_FOLDER = './static/uploads'
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

@app.route('/process_frame', methods=['POST'])
def process_frame():
    file = request.files.get('frame')
    if not file:
        return jsonify({"error": "No frame provided"}), 400

    frame_array = np.frombuffer(file.read(), np.uint8)
    frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)

    if frame is None:
        return jsonify({"error": "Frame could not be decoded"}), 400

    detection_result = detect_objects_in_frame(frame)
    return jsonify({"result": detection_result})

def detect_objects_in_frame(frame):
    return "\nDetected objects in single frame 1"


if __name__ == '__main__':
    app.run(debug=True)