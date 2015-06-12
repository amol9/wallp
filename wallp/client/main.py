import sys

from . import ArgParser
from ..util import log
from ..db import Config, DBError, NotFoundError


#entry point
def main():
	
	argparser = ArgParser()
	argparser.parse_args()

