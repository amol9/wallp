from abc import ABCMeta, abstractmethod
from random import choice

from mutils.system import *


class Service():

	__metaclass__ = ABCMeta

	@abstractmethod
	def get_image(pictures_dir, basename, query=None, color=None):
		pass


class ServiceException(Exception):
	pass


	

