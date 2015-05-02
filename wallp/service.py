from abc import ABCMeta, abstractmethod
from random import choice

from mutils.system import *

'''if is_py3():
	class Service(metaclass=ABCMeta):
		@abstractmethod
		def get_image(pictures_dir, basename, query=None, color=None):
			pass

else:'''
class Service():
	__metaclass__ = ABCMeta

	@abstractmethod
	def get_image(pictures_dir, basename, query=None, color=None):
		pass


class ServiceException(Exception):
	pass


	

