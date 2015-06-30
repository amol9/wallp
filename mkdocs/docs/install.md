# Installation

Use PyPI/pip to install the package.

`>pip install wallp`


### Dependencies:
#### Linux / Windows

 Python packages: (will be automatically installed by pip)

 * praw
 * mutils
 * sqlalchemy
 * zope.interface
 * mayloop
 * six


#### KDE Plasma

 * library: python-dbus or python3-dbus (depending on the version of python you are using).
   E.g. on Ubuntu,
   
   `>apt-get install python-dbus`

 * utility: xdotool

   KDE Plasma makes it impossible to programatically change the wallpaper. This utility is essential for automatic changing of wallpaper.

   `>apt-get install xdotool`


