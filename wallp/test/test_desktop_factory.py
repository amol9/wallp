from unittest import TestCase, main as ut_main

from wallp.desktop.desktop_factory import get_desktop


class TestDesktopFactory(TestCase):

	def test_get_desktop(self):
		d = get_desktop()
		print(type(d))


if __name__ == '__main__':
	ut_main()

