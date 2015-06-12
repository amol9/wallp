
from . import ArgParser
from ..util import log
from ..db import Config


#entry point
def main():
	config = Config()
	log.start(config.get('client.logfile'), loglevel=config.get('client.loglevel'))

	argparser = ArgParser()
	argparser.parse_args()

