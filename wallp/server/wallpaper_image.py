import os


class WallpaperImage():
	def __init__(self):
		self._buffer = None
		self._path = None
		self._chunk_size = 1000
		self._length = None


	def chunk(self, chunk_no):
		if self._path is None:
			raise Exception

		if self._buffer is None:
			try:
				image_file = open(self._path, 'rb')
				self._buffer = image_file.read()
				image_file.close()
			except FileNotFound as e:
				#log
				raise Exception

		chunk = self._buffer[chunk_no * self._chunk_size : self._chunk_size]
		return chunk
	

	def set_path(self, filepath):
		self._length = os.stat(self._path).st_size
		self._chunk_count = int(length / self._chunk_size)
		if self._chunk_count * self._chunk_size < self._length:
			self._chunk_count += 1

		del self._buffer
		self._buffer = None


	def get_path(self):
		return self._path


	def release_buffer(self):
		if self._buffer is not None:
			del self._buffer
			self._buffer = None


	def get_chunk_count(self):
		return self._chunk_count


	def get_length(self):
		return self._length


	path = property(get_path, set_path)
	chunk_count = property(get_chunk_count)
	length = property(get_length)
	
