import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages
import platform

from wallp.globals import Const


entry_points = {}
entry_points['console_scripts'] = ['wallp=wallp.main:main']
if platform.system() == 'Windows':
	entry_points['gui_scripts'] = ['%s=wallp.main:main'%Const.scheduler_cmd]

setup(	name='wallp',
	version='1.0',
	description='Utility to download and set desktop wallpapers from various sources.',
	author='Amol Umrale',
	author_email='babaiscool@gmail.com',
	url='http://pypi.python.org/pypi/wallp/'
	packages=['wallp'],
	scripts=['ez_setup.py'],
	entry_points = entry_points,
	install_requires=['praw']
)

