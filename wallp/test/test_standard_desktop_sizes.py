from unittest import TestCase, main as ut_main

from wallp.desktop.standard_desktop_sizes import StandardDesktopSizes, DesktopSizeException


class TestStandardDesktopSizes(TestCase):
	def test_membership(self):
		sds = StandardDesktopSizes()

		self.assertTrue((800, 600) in sds)
		self.assertTrue((1024, 768) in sds)
		self.assertFalse((800, 60) in sds)
		self.assertFalse((80, 60) in sds)
		self.assertFalse((2342, 6021) in sds)
		self.assertFalse((8000, 60000) in sds)


	def test_nearest(self):
		sds = StandardDesktopSizes()

		self.assertEquals(sds.nearest(800, 700), (800, 600))
		self.assertEquals(sds.nearest(1024, 700), (1024, 768))
		self.assertEquals(sds.nearest(1000, 700), (1024, 768))
		self.assertEquals(sds.nearest(1300, 768), (1280, 800))
		self.assertEquals(sds.nearest(1400, 768), (1366, 768))
		self.assertEquals(sds.nearest(80, 70), (800, 600))
		self.assertEquals(sds.nearest(8000, 7000), (1920, 1200))


	def test_nearest_larger(self):
		sds = StandardDesktopSizes()

		self.assertEquals(sds.nearest_larger(800, 700), (800, 600))
		self.assertEquals(sds.nearest_larger(801, 700), (1024, 768))
		self.assertEquals(sds.nearest_larger(1024, 700), (1024, 768))
		self.assertEquals(sds.nearest_larger(1000, 700), (1024, 768))
		self.assertEquals(sds.nearest_larger(1300, 768), (1366, 768))
		self.assertEquals(sds.nearest_larger(1400, 768), (1440, 900))
		self.assertEquals(sds.nearest_larger(80, 70), (800, 600))
		with self.assertRaises(DesktopSizeException):
			 sds.nearest_larger(8000, 7000)


if __name__ == '__main__':
	ut_main()
i
