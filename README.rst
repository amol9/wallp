=====
wallp
=====

*wallp* selects one of the sources at random, downloads/creates image from it and sets it as desktop wallpaper. 


Supported Sources
=================

**online**

* reddit (subreddits, search)
* bing (gallery)
* google (image search)
* deviantart 
* imgur (search, wallpaper albums, favorites)
* xkcd

**offline**

* single color bitmap
* source code (rendered as image)
  

Supported Platforms
===================

* Python 2.7 / 3.4
* Linux (Gnome or KDE Plasma)
* Windows


Features
========

* Never repeats an image.
* Can schedule the change of wallpaper.
* Editable database of subreddits, imgur albums, search queries to get wallpapers.
* Make a wallpaper stick (no change) for a certain period of time.
* Print detailed info on image, such as, source url, size, path, username, description, etc.
* Can manage favorites.


Usage
=====

Some sample commands::

   wallp                                    # change wallpaper
   wallp source -h                          # list all sources
   wallp schedule add 1h                    # change wallpaper every 1 hour
   wallp info                               # print information about the current wallpaper image

   wallp config dump                        # dump the program configuration
   wallp config disable deviantart          # disable deviantart as a source of images
   wallp config list query add 'linux'      # add 'linux' as a query to be used (at random) when searching for wallpapers
   wallp config list subreddit add pics     # add subreddit pics
   wallp config list imgur-album add SVFae  # add imgur album SVFae
   wallp config set image.max_size 1000000  # limit image size to 1MB

   wallp source imgur wallpaper-album       # select a random wallpaper album from imgur and get a random image from it
   wallp source google -q 'wallpapers'      # query google for 'wallpapers' and get a random image from results

   wallp keep 1d                            # like a wallpaper very much? keep it unchanged for 1 day
   wallp stats                              # print usage stats

   wallp -h                                 # get help 


Download
========

* PyPI: http://pypi.python.org/pypi/wallp
* Source: https://github.com/amol9/wallp

