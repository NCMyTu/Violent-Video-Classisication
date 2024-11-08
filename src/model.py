import numpy as np
import h5py
import tensorflow as tf
from tensorflow.keras import models, Sequential
from tensorflow.keras.layers import Dense, Flatten, InputLayer
from process_feature import resize_feature_to_n_rows

def create_model(input_shape, fc1, fc2):
	return Sequential([
		InputLayer(input_shape=(32, 4096)),
		Flatten(),
		Dense(fc1, activation='relu'),
		Dense(fc2, activation='relu'),
		Dense(1, activation='sigmoid')
	])

def get_tensor(path, label):
	features = []

	with h5py.File(path) as file:
		keys = list(file.keys())
	
		for key in keys:
			feature = np.array(file[key]["c3d_features"])
			feature = resize_feature_to_n_rows(feature, n_rows=32)
			features.append(feature)

	labels = [label] * len(features)

	features = tf.convert_to_tensor(features, dtype=tf.float32)
	labels = tf.convert_to_tensor(labels, dtype=tf.float32)

	return (features, labels)