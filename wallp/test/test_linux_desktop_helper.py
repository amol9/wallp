from unittest import TestCase, main as ut_main

import wallp.linux_desktop_helper as ldh
from wallp.logger import log


class TestLinuxDesktopHelper(TestCase):
	def setUp(self):
		log.enable_testresults()


	def tearDown(self):
		log.clear_testresult()


	def test_set_dbus_vars_if_cron(self):
		orig_is_cron_session = ldh.is_cron_session
		orig_are_dbus_session_vars_set = ldh.are_dbus_session_vars_set

		ldh.is_cron_session = lambda : True
		ldh.are_dbus_session_vars_set = lambda : False

		self.assertTrue(ldh.set_dbus_session_vars_if_cron())

		dbus_addr = log.get_testresult()[0]
		gdmsession = log.get_testresult()[1]
		display = log.get_testresult()[2]

		print 'DBUS_SESSION_BUS_ADDRESS: ', dbus_addr
		self.assertIsNotNone(dbus_addr)
		self.assertRegexpMatches(dbus_addr, 'unix:abstract=/tmp/dbus-\w+')

		print 'GDMSESSION: ', gdmsession
		self.assertIsNotNone(gdmsession)
		self.assertTrue(gdmsession in ['ubuntu', 'gnome', 'kde-plasma'])

		print 'DISPLAY: ', display
		self.assertIsNotNone(display)
		self.assertTrue(len(display) > 0)

		ldh.is_cron_session = orig_is_cron_session
		ldh.are_dbus_session_vars_set = orig_are_dbus_session_vars_set
	

if __name__ == '__main__':
	ut_main()

