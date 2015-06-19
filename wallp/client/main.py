import sys

from .version import __version__
from . import ArgParser
from ..command import Command


#entry point
def main():
	
	#argparser = ArgParser()
	#argparser.parse_args()

	command = Command()
	command.add_version(__version__)
	command.execute()

