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
    data = request.json
    frame_data = data.get('frame')
    print(frame_data)

    if not frame_data:
        return jsonify({"result": "No frame data received"}), 200    

    try:
        header, encoded = frame_data.split(',', 1)
    except ValueError:
        return jsonify({"result": "Invalid frame data format"}), 200

    try:
        decoded_frame = base64.b64decode(encoded)
    except Exception as e:
        return jsonify({"result": f"Decoding error: {str(e)}"}), 200

    np_arr = np.frombuffer(decoded_frame, np.uint8)

    if np_arr.size == 0:
        return jsonify({"result": "Decoded frame is empty"}), 200

    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if frame is None:
        return jsonify({"result": "Could not decode image"}), 200

    # Process the frame (e.g., run inference)
    result = "Processed frame at {} fps".format(16)

    return jsonify({"result": result}), 200

if __name__ == '__main__':
    app.run(debug=True)