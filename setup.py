import ez_setup
#ez_setup.use_setuptools()
from setuptools import setup, find_packages


setup(	
	name='wallp',
	version='1.0',
	description='Utility to download and set desktop wallpapers from various sources.',
	author='Amol Umrale',
	author_email='babaiscool@gmail.com',
	url='https://www.python.org/sigs/distutils-sig/',
	packages=['wallp'],
	scripts=['ez_setup.py'],
	entry_points = {
		'console_scripts': ['wallp=wallp.main:main'],
	},
	install_requires=['praw']
)
