from unittest import TestCase, main as ut_main
from argparse import ArgumentParser

from wallp.client import ArgParser
from wallp. import const


class ArgParserError(Exception):
	pass


class TestArgParser(TestCase):

	@classmethod
	def setUpClass(cls):
		def mock_parse_args(self, args):
			args = args.split()
			if len(args) == 0:
				args.append('change')
			return self._argparser.parse_args(args)

		cls.orig_ArgParser_parse_args = ArgParser.parse_args
		ArgParser.parse_args = mock_parse_args

		def mock_error(self, message):
			raise ArgParserError(message)

		cls.orig_ArgumentParser_error = ArgumentParser.error
		ArgumentParser.error = mock_error


	@classmethod
	def tearDownClass(cls):
		ArgParser.parse_args = cls.orig_ArgParser_parse_args
		ArgumentParser.error = cls.orig_ArgumentParser_error


	def test_version(self):
		argparser = ArgParser()
		with self.assertRaises(SystemExit) as cm:
			argparser.parse_args('-v')
			self.assertEquals(cm.exception.code, 0)

		with self.assertRaises(SystemExit) as cm:
			argparser.parse_args('--version')
			self.assertEquals(cm.exception.code, 0)


	def test_no_subcommand_or_args(self):
		argparser = ArgParser()

		args = argparser.parse_args('')
		self.assertEquals(args.subcommand, 'change')
	

	def test_subcmd_change(self):
		argparser = ArgParser()

		args = argparser.parse_args('change')
		self.assertEquals(args.subcommand, 'change')
		self.assertIsNone(args.service, None)
		self.assertIsNone(args.query)
		self.assertIsNone(args.color)

		args = argparser.parse_args('change -s bitmap')
		self.assertEquals(args.subcommand, 'change')
		self.assertEquals(args.service, 'bitmap')
		self.assertIsNone(args.query)
		self.assertIsNone(args.color)

		args = argparser.parse_args('change -s google -q something -c gray')
		self.assertEquals(args.subcommand, 'change')
		self.assertEquals(args.service, 'google')
		self.assertEquals(args.query, 'something')
		self.assertEquals(args.color, 'gray')


	def test_subcmd_set(self):
		argparser = ArgParser()

		args = argparser.parse_args('set a 10')
		self.assertEquals(args.subcommand, 'set')
		self.assertEquals(args.name, 'a')
		self.assertEquals(args.value, '10')
	
		args = argparser.parse_args('set server hostname')
		self.assertEquals(args.subcommand, 'set')
		self.assertEquals(args.name, 'server')
		self.assertEquals(args.value, 'hostname')


if __name__ == '__main__':
	ut_main()

