from time import time


class Scheduler():
	def __init__(self):
		self._next_run = time() + 5

	def is_ready(self):
		if time() >= self._next_run:
			self._next_run += 100
			return True
		return False
