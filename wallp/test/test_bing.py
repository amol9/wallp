from unittest import TestCase, main as ut_main

from mangoutils.system import *
if is_py3():
	from urllib.error import HTTPError
	from urllib.request import urlopen
else:
	from urllib2 import HTTPError, urlopen

from wallp.bing import Bing
from wallp.standard_desktop_sizes import StandardDesktopSizes


class TestBing(TestCase):

	def test_valid_image_sizes(self):
		bing = Bing()
		std_sizes = StandardDesktopSizes()

		image_names = bing.get_image_names()
		server_url = bing.get_image_server() 

		valid_sizes = []
		for width, height in std_sizes.sizes:
			retries = 10
			for image_name in image_names:
				image_url = 'http:' + server_url + image_name + '_' + str(width) + 'x' + str(height) + '.jpg'
				
				res = None
				try:
					res = urlopen(image_url)
					if res.getcode() != 200:
						raise Exception

					print('success: %s\nvalid size: (%d, %d)'%(image_url, width, height))
					valid_sizes.append((width, height))
					break

				except (Exception, HTTPError) as e:
					print('failed: %s'%image_url)
					if retries == 0:
						break
					retries -= 1
					continue

				res.close()

		print('Result\n------')
		for width, height in valid_sizes:
			print('(%d, %d)'%(width, height))


if __name__ == '__main__':
	ut_main()

