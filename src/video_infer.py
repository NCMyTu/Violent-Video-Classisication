import os
import h5py
import numpy as np
import tensorflow as tf
from process_feature import resize_feature_to_n_rows
from model import create_model, get_tensor
from config import output_dir, video_dir, output_name

video_dir = r"C:\Users\PC MY TU\Desktop"
video_name = "test.mp4"

os.system(f"python ./feature_extractor_vid.py -i \"{video_dir}\" -p {video_name}")

x, _ = get_tensor(os.path.join(output_dir, output_name), label=1)

input_shape = x[0].shape
model = create_model(input_shape)
model.load_weights(r"C:\Users\PC MY TU\Desktop\CS420\trained_2048_512.weights.h5")

y_pred = model.predict(x)
print(f"confidence: {y_pred.reshape(-1)[0]}")