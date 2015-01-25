from unittest import TestCase, main as ut_main
import sys

from wallp.scheduler import get_scheduler
from wallp.globals import Const


class TestScheduler(TestCase):
	def test_parse(self):
		sch = get_scheduler()

		self.assertEquals((1, 'm'), sch.parse('1m'))
		self.assertEquals((1, 'h'), sch.parse('1h'))
		self.assertEquals((14, 'h'), sch.parse('14h'))
		self.assertEquals((3, 'd'), sch.parse('3d'))
		self.assertEquals((1, 'M'), sch.parse('1M'))
		self.assertEquals((1, 'w'), sch.parse('1w'))

		self.assertRaises(Exception, sch.parse, '1u')
		self.assertRaises(Exception, sch.parse, '1000m')
		self.assertRaises(Exception, sch.parse, '')
		self.assertRaises(Exception, sch.parse, 'm')


if __name__ =='__main__':
	if len(sys.argv) > 1:
		if sys.argv[1] == '-d':
			get_scheduler().delete(Const.scheduler_task_name)
		else:
			get_scheduler().schedule(sys.argv[1], 'wallp', Const.scheduler_task_name)
		sys.exit(0)

	ut_main()
