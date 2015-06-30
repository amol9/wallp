# add / enable / disable

wallp supports 3 kinds of lists:

* imgur albums - list of imgur albums 
* subreddits
* search term list - search terms to be used to query services

and 6 services:

* reddit
* bing
* imgur
* deviantart
* google
* bitmap

The "add" command lets you add new items to the lists. While "enable" or "disable" commands let you enable or disable individual items in the list so that they will not be used to get an image for wallpaper. In addition, "enable" or "disable" can also br used to enable or disable a service.

## add

**usage: wallp add list-name item**

Add an item to the list.

 Argument	|
 ---------------|------------------------------------------------------------------
 list-name	| One of: imgur-album, subreddit, search-term.
 item		| Item to be added. (imgur album url /subreddit name / search term)


## enable

**usage: wallp enable name [item]**

Enable an item in the list or a service.

 Argument	|
 ---------------|------------------------------------------------------------------
 name		| If it is a list, one of: imgur-album, subreddit, search-term.
		| Else, must be a service name.
 item		| Item to be enabled. (Not needed for service).


## disable

**usage: wallp disable name [item]**

Disable an item in the list or a service. 

 Argument	|
 ---------------|------------------------------------------------------------------
 name		| If it is a list, one of: imgur-album, subreddit, search-term.
		| Else, must be a service name.	
 item		| Item to be disabled. (Not needed for service).


`>wallp disable deviantart`

`>wallp add search-term 'the big bang theory'`

`>wallp disable subreddit offensive_wallpapers`

`>wallp add imgur-album http://imgur.com/gallery/akHsJ`

`>wallp add subreddit wallpapers`

