import os


class WallpaperImage():
	def __init__(self):
		self._buffer = None
		self._path = None
		self._chunk_size = 1000
		self._length = None
		self._extension = None


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

		start_pos = chunk_no * self._chunk_size
		end_pos = start_pos + self._chunk_size
		end_pos = end_pos if end_pos <= self._length else self._length
		#print 'chunk: %s, start: %d, end: %d'%(chunk_no, start_pos, end_pos)

		chunk = self._buffer[start_pos : end_pos]

		return chunk
	

	def set_path(self, filepath):
		self._path = filepath
		self._length = os.stat(self._path).st_size

		self._chunk_count = int(self._length / self._chunk_size)
		if self._chunk_count * self._chunk_size < self._length:
			self._chunk_count += 1

		self._extension = self._path[self._path.rfind('.') + 1:]
		print 'extension = ', self._extension

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


	def get_extension(self):
		return self._extension


	path = property(get_path, set_path)
	chunk_count = property(get_chunk_count)
	length = property(get_length)
	extension = property(get_extension)
