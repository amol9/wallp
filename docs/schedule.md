# schedule

**usage: wallp schedule command**

Executes the given schedule command.

 Commands	|
 ---------------|-------------------------------------------------------------
 add		| Add schedule to change the wallpaper at specified intervals.
 remove		| Remove the schedule.


## schedule add

**usage: wallp schedule add frequency**

Schedule the wallpaper to be changed at the specified time frequency.

Note: If a schedule already exists, it will be replaced by the new one.

 Argument	|
 ---------------|--------------------------------------------------------------------
 frequency	| Time frequency. {number}{time period identifier}
		| m: minutes, h: hours, d: days, w: weeks, M: months
		| e.g. 1m = every minute, 15m = every 15 minutes, 1h every hour, etc.

`>wallp schedule add 1h`


##schedule remove

**wallp schedule remove**

Remove the schedule.

