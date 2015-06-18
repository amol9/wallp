import sys

from . import ArgParser
from ..command import Command


#entry point
def main():
	
	#argparser = ArgParser()
	#argparser.parse_args()

	command = Command()
	command.execute()

