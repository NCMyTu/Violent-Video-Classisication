import cv2
import shutil
import os

def extract_frames(video_path, FPS=16, output_path="./frames"):
	file_name = os.path.basename(video_path).split(".")[0]
	save_dir = output_path
	if os.path.isdir(save_dir):
		shutil.rmtree(save_dir)
	os.makedirs(save_dir)

	count = 0
	vidcap = cv2.VideoCapture(video_path)
	success, image = vidcap.read()
	success = True

	while success:
		vidcap.set(cv2.CAP_PROP_POS_MSEC, (count/FPS*1000))
		success, image = vidcap.read()

		if image is None:
			print(f"reached the end of video at frame no.{count+1:05}")
			break

		save_path = os.path.join(save_dir, f"image_{count+1:05}.jpg")
		cv2.imwrite(save_path, image)
		print(f"extracted frame no.{count+1:05}")
		count += 1

video_path = r"C:\Users\PC MY TU\Desktop\test.mp4"
extract_frames(video_path)