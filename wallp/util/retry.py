from time import sleep


class Retry:
	def __init__(self, retries=3, delay=None, final_exc=None, exp_bkf=True):
		self.retries = retries
		self.delay = delay
		self.final_exc = final_exc
		self.exp_bkf = exp_bkf


	def retry(self, exception=None):
		self.retries -= 1

		if self.retries == 0:
			if exception is not None:
				raise exception
			if self.final_exc is not None:
				raise self.final_exc
			return


		if self.delay is not None:
			sleep(self.delay)
			self.delay *= 2 if self.exp_bkf else 1


	def left(self):
		return self.retries > 0


	def cancel(self):
		self.retries = 0

