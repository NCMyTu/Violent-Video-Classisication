import numpy as np
import tensorflow as tf
import h5py
from model import create_model, get_tensor
from process_feature import resize_feature_to_n_rows

violent_dir = r"C:\Users\PC MY TU\Desktop\CS420\data\extracted_feature\test_violent.hdf5"
non_violent_dir = r"C:\Users\PC MY TU\Desktop\CS420\data\extracted_feature\test_non_violent.hdf5"

f_violent, l_violent = get_tensor(violent_dir, label=1)
f_non_violent, l_non_violent = get_tensor(non_violent_dir, label=0)

x = tf.concat([f_violent, f_non_violent], axis=0)
y = tf.concat([l_violent, l_non_violent], axis=0)

input_shape = x[0].shape
model = create_model(input_shape)
model.load_weights(r"C:\Users\PC MY TU\Desktop\CS420\trained_2048_512.weights.h5")

y_pred_violent = []
with h5py.File(violent_dir) as file:
	keys = list(file.keys())

	for key in keys:
		feature = np.array(file[key]["c3d_features"])
		feature = [resize_feature_to_n_rows(feature, n_rows=32)]
		feature = tf.convert_to_tensor(feature, dtype=tf.float32)
		y_pred = model.predict(feature)
		y_pred_violent.append((y_pred, key))

y_pred_non_violent = []
with h5py.File(non_violent_dir) as file:
	keys = list(file.keys())

	for key in keys:
		feature = np.array(file[key]["c3d_features"])
		feature = [resize_feature_to_n_rows(feature, n_rows=32)]
		feature = tf.convert_to_tensor(feature, dtype=tf.float32)
		y_pred = model.predict(feature)
		y_pred_non_violent.append((y_pred, key))

y_pred = model.predict(x)

thresh = 0.5

for res in y_pred_violent:
	if res[0][0][0] < thresh:
		print(f"video: {res[1]}, predicted: {res[0][0][0]:.4f}, ground_truth: 1")

for res in y_pred_non_violent:
	if res[0][0][0] >= thresh:
		print(f"video: {res[1]}, predicted: {res[0][0][0]:.4f}, ground_truth: 0")

y_pred = (y_pred.reshape(-1) >= thresh).astype(int)
acc = np.mean(y == y_pred)

print(f"\naccuracy: {acc:.4f}")