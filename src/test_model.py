import numpy as np
import tensorflow as tf
from model import create_model, get_tensor

f_violent, l_violent = get_tensor(r"extracted_features\video\test_violent.hdf5", label=1)
f_non_violent, l_non_violent = get_tensor(r"extracted_features\video\test_non_violent.hdf5", label=0)

x = tf.concat([f_violent, f_non_violent], axis=0)
y = tf.concat([l_violent, l_non_violent], axis=0)

input_shape = x[0].shape
model = create_model(input_shape, 2048, 512)
model.load_weights("trained_2048_512.weights.h5")

y_pred = model.predict(x)

y_pred = (y_pred.reshape(-1) > 0.5).astype(int)
acc = np.mean(y == y_pred)

print(f"accuracy: {acc:.4f}")