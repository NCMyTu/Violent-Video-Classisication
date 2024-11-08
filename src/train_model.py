import numpy as np
import tensorflow as tf
from model import create_model, get_tensor

f_violent, l_violent = get_tensor(r"extracted_features\video\train_violent.hdf5", label=1)
f_non_violent, l_non_violent = get_tensor(r"extracted_features\video\train_non_violent.hdf5", label=0)

x = tf.concat([f_violent, f_non_violent], axis=0)
y = tf.concat([l_violent, l_non_violent], axis=0)
dataset = tf.data.Dataset.from_tensor_slices((x, y))
dataset = dataset.shuffle(buffer_size=10000)
dataset = dataset.batch(32)

input_shape = x[0].shape
model = create_model(input_shape, 2048, 512)
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model.summary()

model.fit(dataset, epochs=10)

