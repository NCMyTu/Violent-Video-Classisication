import cv2
import time
import sys
import os
import numpy as np
import torch
import tensorflow as tf
from tensorflow.keras.models import load_model
from torch.autograd import Variable
from skimage.transform import resize
from flask import Flask, render_template, request, jsonify, url_for
from flask_socketio import SocketIO, emit
from threading import Thread, Event
import queue
from collections import deque
# sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
# from process_feature import resize_feature_to_n_rows
# from model import create_model
# from C3D_model import C3D

UPLOAD_FOLDER = './static/uploads'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
socketio = SocketIO(app, cors_allowed_origins="*")

fps = 16
BATCH_SIZE = fps * 1
frame_time = 1 / fps
crop_w = 64 # 112
crop_h = 64 # 112
frame_queue = queue.Queue()

# thread control events
stop_event = Event()

# c3d = C3D(487)
# classifier = create_model((32, 4096))
# classifier.load_weights(r"C:\Users\PC MY TU\Desktop\CS420\trained_2048_512_2.weights.h5")
mobi_lstm = load_model(r"C:\Users\PC MY TU\Desktop\Mobi_LSTM\mobi_lstm.keras")

def extract_feature(imgs):
	imgs = np.array(imgs, dtype="float32")
	imgs = torch.from_numpy(np.float32(imgs.transpose(0, 4, 1, 2, 3)))
	imgs = Variable(imgs)
	_, batch_output = c3d(imgs, 6)
	batch_feature  = (batch_output.data).cpu()
	features = batch_feature.numpy()
	features = resize_feature_to_n_rows(features)
	features = tf.convert_to_tensor([features], dtype=tf.float32)
	return features

def _predict_video(video_file_path, model):
	SEQUENCE_LENGTH = 16
	IMAGE_WIDTH, IMAGE_HEIGHT = 64, 64

	video_reader = cv2.VideoCapture(video_file_path)
	
	video_frames_count = int(video_reader.get(cv2.CAP_PROP_FRAME_COUNT))
	skip_frames_window = max(int(video_frames_count/SEQUENCE_LENGTH),1)

	frames_list = []
	for frame_counter in range(SEQUENCE_LENGTH):
		video_reader.set(cv2.CAP_PROP_POS_FRAMES, frame_counter * skip_frames_window)
 
		success, frame = video_reader.read() 
 
		if not success:
			break
 
		frame = cv2.resize(frame, (IMAGE_HEIGHT, IMAGE_WIDTH))
		frame = frame / 255
	  
		frames_list.append(frame)
 
	y_pred = model.predict(np.expand_dims(frames_list, axis = 0), verbose=0)[0]
	label = np.argmax(y_pred)
	conf_score = y_pred[label]

	return label, conf_score

def process_features_worker():
	while not stop_event.is_set():
		try:
			imgs, received_time = frame_queue.get(timeout=5)
			if imgs is None:
				break

			# features = extract_feature(imgs)
			# y_pred = classifier.predict(features)
			# conf_score = y_pred[0][0]
			# print(f"Confidence: {conf_score:.4f}")

			imgs = np.array(imgs)
			y_pred = mobi_lstm.predict(imgs, verbose=0)
			conf_score = np.max(y_pred[0])
			prediction = int(np.argmax(y_pred)) # int64, wtf tf?

			_, buffer = cv2.imencode('.jpg', imgs[-1][-1])
			img_bytes = buffer.tobytes()
			socketio.emit('update_frame', {
											'image': img_bytes,
											"is_prediction": True,
											"prediction": prediction,
											'confidence': float(conf_score),
											"timestamp": received_time
											}
						)

		except queue.Empty:
			continue
		except Exception as e:
			print(f"Error in feature processing thread: {e}")

def cctv_processing(stream_url):
	cap = cv2.VideoCapture(stream_url)

	if not cap.isOpened():
		print("Error: Unable to open stream")
		exit()

	frames = []
	current_time = None
	while not stop_event.is_set():
		start_time = time.time()

		while cap.isOpened() and not stop_event.is_set():
			_, frame = cap.read()
		   
			if time.time() - start_time >= frame_time:
				break

		if stop_event.is_set():
			break
		
		if len(frames) < BATCH_SIZE:
			_, buffer = cv2.imencode('.jpg', frame)
			img_bytes = buffer.tobytes()
			# send image to frontend
			socketio.emit('update_frame', {
											'image': img_bytes, 
											"is_prediction": False
											}
						)
			frames.append(frame)

			if len(frames) == 1:
				current_time = time.strftime("%H:%M:%S %d/%m/%Y")
		elif len(frames) >= BATCH_SIZE:
			imgs = []
			for i in range(0, len(frames), fps):
				img = np.array(
								[
									resize(
										frame,
										output_shape=(crop_w, crop_h), 
										preserve_range=True
										).astype(np.float64)
									for frame in frames[i:i+fps]
								]
								)
				img /= 225.0
				imgs.append(img)

			# cv2.imshow("Live Stream", cv2.cvtColor(imgs[0][-1], cv2.COLOR_RGB2BGR))

			frame_queue.put((imgs, current_time))
			frames = []

		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

		# wait to match the exact frame time
		elapsed_time = time.time() - start_time
		time_to_wait = max(0, frame_time - elapsed_time)
		time.sleep(time_to_wait)

	cap.release()  # Release the camera resource
	cv2.destroyAllWindows()
	print("-----> CCTV stream disconnected")

@app.route("/")
def index():
	return render_template("index.html")

@app.route('/upload_video', methods=['POST'])
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

@app.route("/predict_video", methods=["POST"])
def predict_video():
	data = request.get_json()
	video_url = data.get('video_url')

	if not video_url:
		return jsonify({"error": "Video URL is missing."}), 400

	label, conf_score = _predict_video(video_url, mobi_lstm)

	return jsonify({
		"label": int(label),
		"conf_score": float(conf_score)
		})

@socketio.on('start_cctv')
def start_cctv(data):
	stream_url = data.get('stream_url')
	print(f"-----> Received stream URL: {stream_url}")

	global stop_event
	stop_event.clear()  # reset the stop event

	feature_thread = Thread(target=process_features_worker)
	feature_thread.daemon = True
	feature_thread.start()
	
	cctv_thread = Thread(target=cctv_processing, args=(stream_url,))
	cctv_thread.daemon = True
	cctv_thread.start()

@socketio.on('stop_cctv')
def stop_cctv():
	print("-----> Stopping CCTV stream")
	
	global stop_event
	stop_event.set()  # set the stop event
	
	frame_queue.put(None)


if __name__ == "__main__":
	socketio.run(app, host="0.0.0.0", port=5000, debug=True)