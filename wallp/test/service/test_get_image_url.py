from unittest import TestCase, main as ut_main
from random import random

from wallp.service import Imgur, Google, DeviantArt, Reddit, Bing
from wallp.util import log
from wallp.db import func as dbfunc


class TestGetImageUrl(TestCase):
	image_url_seen_ratio = 0
	interactive = True

	@classmethod
	def setUpClass(cls):
		log.start('stdout', log.levels['debug'])

		cls.orig_image_url_seen = dbfunc.image_url_seen
		dbfunc.image_url_seen = lambda x : random() < cls.image_url_seen_ratio


	@classmethod
	def tearDownClass(cls):
		dbfunc.image_url_seen = cls.orig_image_url_seen


	def print_info(self, image_trace, image_source):
		print('')
		for step in image_trace:
			print("{0}. {1:<25}: {2}".format(step.step, step.name, step.data))
		print('source info:')
		print(image_source)


	def service_get_image_url(self, service):
		url = service.get_image_url()

		if self.interactive:
			print url
			self.print_info(service.image_trace, service.image_source)

		self.assertGreater(len(service.image_trace), 0)


	def test_imgur(self):
		self.service_get_image_url(Imgur())


	def test_google(self):
		self.service_get_image_url(Google())


	def test_deviantart(self):
		self.service_get_image_url(DeviantArt())


	def test_reddit(self):
		self.service_get_image_url(Reddit())


	def test_bing(self):
		self.service_get_image_url(Bing())


if __name__ == '__main__':
	ut_main()

