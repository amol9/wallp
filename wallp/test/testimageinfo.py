from unittest import TestCase, main as ut_main
import sys

from wallp.imageinfo import get_image_info


class TestImageInfo(TestCase):
	def setUp(self):
		pass


	def test_get_image_info(self):
		pass


if __name__ == '__main__':
	if len(sys.argv) > 1:
		with open(sys.argv[1], 'r') as f:
			ct, w, h = get_image_info(f.read(10000))
			print(('type:', ct, 'width:', w, 'height:', h))
		sys.exit(0)

	ut_main()		
