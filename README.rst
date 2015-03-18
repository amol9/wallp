=====
wallp
=====

This utility selects an online / offline source at random, gets a random image and sets it as a wallpaper.


Features
========
* Supported platforms: Linux / Windows / Python 2.7 / Python 3.x.
* Downloads images from various sources.

  Online:
    * reddit
    * imgur
    * bing (gallery)
    * google images
    * deviantart

  Offline:
    * bitmap (a single color bitmap is generated)

* Allows scheduling of change of wallpaper, viz., every 5 minutes, every 1 hour, etc.
* Can download image based on a query.  

Usage
=====
#. Change wallpaper by selecting a source at random::

	wallp

#. Query for "linux wallpapers" and set a random image as wallpaper from results::

	wallp -s google -q "linux wallpapers"
	wallp -s imgur -q "linux wallpapers"

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
* PyPI: http://pypi.python.org/pypi/wallp
* Source: https://github.com/amol9/wallp

