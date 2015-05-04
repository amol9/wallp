from time import time


class Scehduler():
	def __init__(self):
		self._next_run = time() + 5

	def is_ready(self):
		if time() >= self._next_run:
			return True
		return False
