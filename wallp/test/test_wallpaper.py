from unittest import TestCase, main as ut_main

from wallp.wallpaper import Wallpaper


class TestWallpaper(TestCase):

	def test_change(self):
		wp = Wallpaper()
		wp.change()


if __name__ == '__main__':
	ut_main()

