import ez_setup
ez_setup.use_setuptools()

import platform
import sys
from setuptools import setup, find_packages

from wallp.version import __version__


entry_points = {}
entry_points['console_scripts'] = ['wallp=wallp.main:main']
if platform.system() == 'Windows':
	entry_points['gui_scripts'] = ['wallps=wallp.main:main']

setup(	
	name			= 'wallp',
	version			= __version__,
	description		= 'A command line utility to download/create and set wallpapers from various sources.',
	author			= 'Amol Umrale',
	author_email 		= 'babaiscool@gmail.com',
	url			= 'http://pypi.python.org/pypi/wallp/',
	packages		= find_packages(),
	include_package_data	= True,
	scripts			= ['ez_setup.py'],
	entry_points 		= entry_points,
	install_requires	= ['praw>=3.3.0', 'sqlalchemy>=1.0.12', 'zope.interface', 'mayloop', 'six', 'redcmd>=1.2.10',
					'redlib>=1.5.6', 'giraf>=1.0.16', 'asq>=1.2.1', 'alembic>=0.8.5', 'enum34>=1.1.2',
					'Pillow>=3.1.1', 'Pygments>=2.1.3'],
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

