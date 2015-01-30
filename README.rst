=====
wallp
=====

A command line utility to download and set wallpapers from various sources. 


Features
========
* Works on Linux / Windows.
* Downloads images from various sources. Currently supported sources: reddit, imgur, bing (gallery), google images, deviantart.
* Can set plain bitmap as wallpaper.
* Allows scheduling of change of wallpaper, viz., every 5 minutes, every 1 hour, etc.
* Can download images based on a query.  

Usage
=====
#. Change wallpaper by selecting a source at random::

	wallp

#. Query google images for "linux wallpapers" and set a random image as wallpaper from results::

	wallp -s google -q "linux wallpapers"

#. Set a plain blue colored bitmap as wallpaper::

	wallp -s bitmap -c blue

#. Schedule change of wallpaper:

	every 5 minutes::

		wallp -f 5m

	every 1 hour::

		wallp -f 1h

	every 2 days::

		wallp -f 2d

	remove schedule::

		wallp -f 0

#. For more options, get help::

	wallp -h

Download
========
* PyPI: http://pypi.python.org/pypi/wallp/

