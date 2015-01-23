from unittest import TestCase, main as ut_main
import sys
from os.path import join as joinpath, abspath

from wallp.manager import Manager
from wallp.bitmap import Bitmap


class TestManager(TestCase):
	def test_bitmap(self):
		bmp = Bitmap()
		bmpfile = bmp.get_image('.', 'test', color='0xFF0000')
		filepath = abspath(joinpath('.', bmpfile))

		Manager.__init__ = lambda *args: None
		mgr = Manager()
		mgr._wp_path = filepath
		mgr.set_as_wallpaper()		


if __name__ == '__main__':
	if len(sys.argv) > 1:
		Manager.__init__ = lambda *args: None
		mgr = Manager()
		mgr._wp_path = abspath(sys.argv[1])
		mgr.set_as_wallpaper()
	
		sys.exit(0)

	ut_main()
