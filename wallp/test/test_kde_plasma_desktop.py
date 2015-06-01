from unittest import TestCase, main as ut_main
from os.path import exists, abspath, join as joinpath
from os import mkdir
from shutil import rmtree

from wallp.desktop.kde_plasma_desktop import KdePlasmaDesktop
from wallp.service.bitmap import Bitmap
from wallp.util.config import config
from wallp.globals import Const


class TestKdePlasmaDesktop(TestCase):
	def setUp(self):
		self._testdir = './test123'
		if not exists(self._testdir):
			mkdir(self._testdir)


	def tearDown(self):
		if exists(self._testdir):
			rmtree(self._testdir)


	def test_set_wallpaper(self):
		pics_dir = '/home/amol/Pictures'
		bmp = Bitmap()
		image_filename = bmp.get_image(pics_dir, 'wallp')

		kpd = KdePlasmaDesktop()
		kpd.set_wallpaper(joinpath(pics_dir, image_filename), style='tiled')


	def set_wallpaper_style(self, style):
		kpd = KdePlasmaDesktop()
		kpd.set_wallpaper_style(style)


	def test_set_wallpaper_style_tiled(self):
		self.set_wallpaper_style('tiled')


	def test_set_wallpaper_style_scaled(self):
		self.set_wallpaper_style('scaled')


if __name__ == '__main__':
	ut_main()



		
