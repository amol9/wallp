from abc import ABCMeta, abstractmethod
from random import choice
from zope.interface import Interface, Attribute

from mutils.system import *


class IService(Interface):
	name = Attribute('string identifier')


class IHttpService(IService):

	def get_image_url(query=None, color=None):
		'Get image url.'


class IImageGenService(IService):

	def get_image(query=None, color=None):
		'Get image.'

	def get_extension():
		'Get extension of generated image.'


class ServiceError(Exception):
	pass


	

