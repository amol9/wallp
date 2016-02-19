from unittest import TestCase, main as ut_main

from wallp.desktop.wpstyle import WPStyle, WPStyleError, compute_style


class TestWPStyle(TestCase):

	def test_compute_style(self):
		cs = lambda a, b, c, d : int(compute_style(a, b, c, d))

		dt_size = (1366, 768)

		self.assertEqual(cs(100, 100, *dt_size), WPStyle.TILED)
		self.assertEqual(cs(101, 101, *dt_size), WPStyle.CENTERED)
		self.assertEqual(cs(1366, 768, *dt_size), WPStyle.CENTERED)
		self.assertEqual(cs(1300, 730, *dt_size), WPStyle.SCALED)


if __name__ == '__main__':
	ut_main()

