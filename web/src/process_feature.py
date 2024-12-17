import numpy as np

def _resize_small_feature_to_n_rows(input_feature, n_rows=32):
	resized_feature = []
	f_rows = input_feature.shape[0]
	
	d = n_rows // f_rows
	r = n_rows % f_rows
	start = (f_rows - r) // 2 if r != 0 else None
	end = start + r - 1 if r != 0 else None
	is_overlapped = True if r != 0 else False

	if start == 0:
		start += 1
		end += 1

	for i in range(f_rows):
		# this is faster than using numpy most of the time
		if is_overlapped and start <= i <= end:
			resized_feature.append(np.mean(input_feature[i-1:i+1], axis=0))

		for j in range(i*d, i*d+d):
			resized_feature.append(np.mean(input_feature[i:i+1], axis=0))

	return np.array(resized_feature)

def _resize_small_feature_to_n_rows_np(input_feature, n_rows=32):
	resized_feature = np.empty((0, 4096), dtype=np.float32)
	f_rows = input_feature.shape[0]
	
	d = n_rows // f_rows
	r = n_rows % f_rows
	start = (f_rows - r) // 2 if r != 0 else None
	end = start + r - 1 if r != 0 else None
	is_overlapped = True if r != 0 else False

	if start == 0:
		start += 1
		end += 1

	for i in range(f_rows):
		if is_overlapped and start <= i <= end:
			resized_feature = np.vstack([resized_feature, np.mean(input_feature[i-1:i+1], axis=0)])

		for j in range(i*d, i*d+d):
			resized_feature = np.vstack([resized_feature, np.mean(input_feature[i:i+1], axis=0)])
	
	return resized_feature

def _resize_large_feature_to_n_rows(input_feature, n_rows=32):
	resized_feature = []
	f_rows = input_feature.shape[0]
	
	d = f_rows // n_rows
	r = f_rows % n_rows
	start = (n_rows - r) // 2 if r != 0 else None
	end = start + r - 1 if r != 0 else None
	is_overlapped = True if r != 0 else False
	p = 0

	for i in range(n_rows):
		l = p
		h = p + d - 1

		if is_overlapped and start <= i <= end:
			h += 1

		# still faster than using numpy
		resized_feature.append(np.mean(input_feature[l:h+1], axis=0))

		p = h + 1
	
	return np.array(resized_feature)
	
def _resize_large_feature_to_n_rows_np(input_feature, n_rows=32):
	resized_feature = np.empty((0, 4096), dtype=np.float32)
	f_rows = input_feature.shape[0]
	
	d = f_rows // n_rows
	r = f_rows % n_rows
	start = (n_rows - r) // 2 if r != 0 else None
	end = start + r - 1 if r != 0 else None
	is_overlapped = True if r != 0 else False
	p = 0

	for i in range(n_rows):
		l = p
		h = p + d - 1

		if is_overlapped and start <= i <= end:
			h += 1

		resized_feature = np.vstack([resized_feature, np.mean(input_feature[l:h+1], axis=0)])

		p = h + 1
	
	return resized_feature
	
def resize_feature_to_n_rows(input_feature, n_rows=32):
	"""
	Convert feature of size (k, 4096) to size (32, 4096)
	
	Parameters:
		in_feature: input feature, a numpy array
	Returns:
		resized feature
	"""
	if input_feature.shape[0] < n_rows:
		return _resize_small_feature_to_n_rows(input_feature, n_rows)

	if input_feature.shape[0] > n_rows:
		return _resize_large_feature_to_n_rows(input_feature, n_rows)

	return input_feature

def resize_feature_to_n_rows_np(input_feature, n_rows=32):
	"""
	Numpy version
	Convert feature of size (k, 4096) to size (32, 4096)
	
	Parameters:
		in_feature: input feature
	Returns:
		resized feature
	"""
	
	if input_feature.shape[0] < n_rows:
		return _resize_small_feature_to_n_rows_np(input_feature, n_rows)

	if input_feature.shape[0] > n_rows:
		return _resize_large_feature_to_n_rows_np(input_feature, n_rows)

	return input_feature