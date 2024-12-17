import cv2
import time
import sys
import os
import numpy as np
import torch
import tensorflow as tf
from torch.autograd import Variable
from skimage.transform import resize
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from threading import Thread, Event
import secrets
import queue

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from process_feature import resize_feature_to_n_rows
from model import create_model
from C3D_model import C3D

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

fps = 16
BATCH_SIZE = fps * 1
frame_time = 1 / fps
crop_w = 112
crop_h = 112
frame_queue = queue.Queue()

# thread control events
stop_event = Event()

# stream_url = "http://192.168.1.49:4747/video"
c3d = C3D(487)
classifier = create_model((32, 4096))
classifier.load_weights(r"C:\Users\PC MY TU\Desktop\CS420\trained_2048_512_2.weights.h5")

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

def process_features_worker():
	while not stop_event.is_set():
		try:
			imgs, received_time = frame_queue.get(timeout=5)
			if imgs is None:
				break

			features = extract_feature(imgs)
			y_pred = classifier.predict(features)
			conf_score = y_pred[0][0]
			print(f"Confidence: {conf_score:.4f}")

			_, buffer = cv2.imencode('.jpg', imgs[-1][-1])
			img_bytes = buffer.tobytes()
			socketio.emit('update_frame', {
											'image': img_bytes,
											'confidence': float(conf_score),
											"timestamp": received_time
											})

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

		# capture frame
		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
		
		if len(frames) < BATCH_SIZE:
			_, buffer = cv2.imencode('.jpg', frame)
			img_bytes = buffer.tobytes()
			socketio.emit('update_frame', {'image': img_bytes, 'confidence': None})
			frames.append(frame)

			if len(frames) == 1:
				current_time = time.strftime("%H:%M:%S %d-%m-%Y")
		elif len(frames) >= BATCH_SIZE:
			imgs = []
			for i in range(0, len(frames), fps):
				img = np.array(
								[
									resize(
										frame,
										output_shape=(crop_w, crop_h), 
										preserve_range=True
										).astype(np.uint8)
									for frame in frames[i:i+fps]
								]
								)
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
	print("-----> Camera stream disconnect")

@app.route("/")
def index():
	return render_template("index.html")

@socketio.on('start_cctv')
def start_cctv(data):
	stream_url = data.get('stream_url')  # Retrieve the stream URL from the client
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
	stop_event.set()  # Reset the stop event
	
	frame_queue.put(None)


if __name__ == "__main__":
	socketio.run(app, host="0.0.0.0", port=5000, debug=True)