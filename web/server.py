import os
import cv2
import numpy as np
from threading import Lock
import base64
from flask import Flask, render_template, request, url_for, jsonify

UPLOAD_FOLDER = './static/uploads'
BATCH_SIZE = 32
frame_batch = []
batch_lock = Lock()

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
    global frame_batch
    data = request.get_json()

    if not data or 'frame' not in data or 'height' not in data or 'width' not in data:
        return jsonify({"error": "Incomplete frame data received"}), 400

    try:
        frame_data = base64.b64decode(data['frame'])
        np_frame = np.frombuffer(frame_data, dtype=np.uint8)

        expected_size = data['height'] * data['width'] * 3
        print(f"w: {data['width']}, h: {data['height']}")
        if np_frame.size != expected_size:
            print(f"size mismatched: expected {expected_size}, got {np_frame.shape}")

        frame = np_frame.reshape((data['height'], data['width'], 3))

    except Exception as e:
        return jsonify({"error": f"Invalid frame data: {str(e)}"}), 400

    with batch_lock:
        frame_batch.append(frame)
        if len(frame_batch) < BATCH_SIZE:
            return jsonify({"message": f"Frame added to batch ({len(frame_batch)}/{BATCH_SIZE})"})
        
        batch_results = process_batch(frame_batch)
        frame_batch = []

    return jsonify({"message": "Batch processed", "results": batch_results})

def process_batch(batch):
    results = []
    for i, frame in enumerate(batch):
        height, width, _ = frame.shape
        detection = {
            "frame_id": i,
            "bbox": [0.1 * width, 0.1 * height, 0.8 * width, 0.8 * height],
            "confidence": 0.95
        }
        results.append(detection)
    return results


if __name__ == '__main__':
    app.run(debug=True)