import cv2
import time
import os
import numpy as np
from tensorflow.keras.models import load_model

def frames_extraction(video_path):
	SEQUENCE_LENGTH = 16
	frames_list = []

	video_reader = cv2.VideoCapture(video_path)
	
	video_frames_count = int(video_reader.get(cv2.CAP_PROP_FRAME_COUNT))

	skip_frames_window = max(int(video_frames_count/SEQUENCE_LENGTH), 1)
 
	for frame_counter in range(SEQUENCE_LENGTH):
		# set frame position
		video_reader.set(cv2.CAP_PROP_POS_FRAMES, frame_counter * skip_frames_window)
  
		success, frame = video_reader.read() 
 
		if not success:
			break
 
		resized_frame = cv2.resize(frame, (64, 64))
		
		normalized_frame = resized_frame / 255
		
		frames_list.append(normalized_frame)
 
	video_reader.release()
 
	return frames_list

def predict(model, video_path):
	frames_list = frames_extraction(video_path)
	y_pred = model.predict(np.expand_dims(frames_list, axis = 0), verbose=0)[0]
	label = np.argmax(y_pred)
	return label 


model_path = r"C:\Users\PC MY TU\Desktop\CS420\data\cnn_lstm.keras"
cnn_lstm = load_model(model_path)

violent_dir = [r"C:\Users\PC MY TU\Desktop\child_abuse\train\violent", 
				r"C:\Users\PC MY TU\Desktop\child_abuse\test\violent"]
non_violent_dir = [r"C:\Users\PC MY TU\Desktop\child_abuse\train\non-violent", 
					r"C:\Users\PC MY TU\Desktop\child_abuse\test\non-violent"]


violent_paths = []
non_violent_paths = []

for v_dir in violent_dir:
	for file_name in os.listdir(v_dir):
		path = os.path.join(v_dir, file_name)
		violent_paths.append(path)

for nv_dir in non_violent_dir:
	for file_name in os.listdir(nv_dir):
		path = os.path.join(nv_dir, file_name)
		non_violent_paths.append(path)

y = [1] * len(violent_paths) + [0] * len(non_violent_paths)
y_pred = [predict(cnn_lstm, path) for path in violent_paths] + [predict(cnn_lstm, path) for path in non_violent_paths]

accuracy = sum([1 for true, pred in zip(y, y_pred) if true == pred]) / len(y)
print(f"Accuracy: {accuracy * 100:.2f}%")