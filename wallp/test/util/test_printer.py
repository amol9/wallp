from unittest import TestCase, main as ut_main
from time import sleep

from wallp.util.printer import Printer


class TestPrinter(TestCase):

	def test_hash_progress(self):
		def hash_progress_maker(pcb, pcp):
			for i in range(0, 10):
				sleep(0.3)
				pcb('#' * i)
			pcp()

		self.g_test_print_progress(hash_progress_maker)


	def test_percentage_progress(self):
		def percentage_pm(pcb, pcp):
			for i in range(0, 100):
				sleep(0.03)
				pcb('%d %%'%(i+1))
			pcp()

		self.g_test_print_progress(percentage_pm)


	def g_test_print_progress(self, pm):
		printer = Printer()
		printer.printf('doing something', '')
		pcb, pcp = printer.printf('making progress', '3s', progress=True, percentage_cb=False)
		pm(pcb, pcp)
		printer.printf('done', '')



if __name__ == '__main__':
	ut_main()

