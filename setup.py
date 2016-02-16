import ez_setup
ez_setup.use_setuptools()

import platform
import sys
from setuptools import setup, find_packages

from rc_setup import setup_autocomp

from wallp.version import __version__


entry_points = {}
entry_points['console_scripts'] = ['wallp=wallp.client.main:main']
if platform.system() == 'Windows':
	entry_points['gui_scripts'] = ['wallps=wallp.client.main:main']


setup(	
	name			= 'wallp',
	version			= __version__,
	description		= 'A command line utility to download and set wallpapers from various sources.',
	author			= 'Amol Umrale',
	author_email 		= 'babaiscool@gmail.com',
	url			= 'http://pypi.python.org/pypi/wallp/',
	packages		= find_packages(),
	include_package_data	= True,
	scripts			= ['ez_setup.py', 'rc_setup.py'],
	entry_points 		= entry_points,
	install_requires	= ['praw', 'mutils', 'sqlalchemy', 'zope.interface', 'mayloop', 'six', 'redcmd>=1.1.3', 'redlib>=1.1.0'],
	classifiers		= [
					'Development Status :: 4 - Beta',
					'Environment :: Console',
					'License :: OSI Approved :: MIT License',
					'Natural Language :: English',
					'Operating System :: POSIX :: Linux',
					'Operating System :: Microsoft :: Windows',
					'Programming Language :: Python :: 2.7',
					'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
					'Topic :: Multimedia :: Graphics'
				]
)

setup_autocomp('wallp.command.all_subcommands', 'wallp', _to_hyphen=True)

