from unittest import TestLoader
import sys


current_testCaseClass = None

def new_TestLoader_loadTestsFromTestCase(self, testCaseClass):
	global current_testCaseClass
	current_testCaseClass = testCaseClass

	return orig_TestLoader_loadTestsFromTestCase(self, testCaseClass)


orig_TestLoader_loadTestsFromTestCase = TestLoader.loadTestsFromTestCase
TestLoader.loadTestsFromTestCase = new_TestLoader_loadTestsFromTestCase


def cmp_testcase_order(self, tc1, tc2):
	func1 = getattr(current_testCaseClass, tc1)
	func2 = getattr(current_testCaseClass, tc2)

	if getattr(func1, '__order__', None) is None or getattr(func2, '__order__', None) is None:
		return 0

	return func1.__order__ - func2.__order__


orig_TestLoader_sortTestMethodsUsing = None


def replace_default_testcase_sort_order():
	orig_TestLoader_sortTestMethodsUsing = TestLoader.sortTestMethodsUsing
	TestLoader.sortTestMethodsUsing = cmp_testcase_order


def restore_default_testcase_sort_order():
	TestLoader.sortTestMethodsUsing = orig_TestLoader_sortTestMethodsUsing


def order(i):
	'Decorator to set test case order.'

	def new_dec(func):
		func.__order__ = i
		return func

	return new_dec


def enable_testcase_ordering(cls):
	'Class decorator to enable test case ordering for a test class.'

	orig_setUpClass = cls.setUpClass

	@classmethod
	def new_setUpClass(kls):
		replace_default_testcase_sort_order()
		orig_setUpClass()


	cls.setUpClass = new_setUpClass

	orig_tearDownClass = cls.tearDownClass

	@classmethod
	def new_tearDownClass(kls):
		restore_default_testcase_sort_order()
		orig_tearDownClass()

	cls.tearDownClass = new_tearDownClass

	return cls
