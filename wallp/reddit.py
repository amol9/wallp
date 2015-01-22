import praw
from os.path import join as joinpath
from random import randint

from wallp.service import Service, service_factory, ServiceException
from wallp.imgur import Imgur
import wallp.web as web
from wallp.config import config
from wallp.globals import Const
from wallp.logger import log


subreddit_list =	['earthporn', 'wallpapers', 'wallpaperdump', 'specart', 'quotesporn', 'offensive_wallpapers',
		 	 'backgroundart', 'desktoplego', 'wallpaper', 'animewallpaper', 'nocontext_wallpapers',
			 'musicwallpapers', 'comicwalls',
			 'ImaginaryLandscapes+ImaginaryMonsters+ImaginaryCharacters+ImaginaryTechnology']
posts_limit = 10


class Reddit(Service):
	name = 'reddit'

	def __init__(self):
		self._subreddit_list = config.get_list('reddit', 'subreddit_list', default=subreddit_list)


	def get_image(self, pictures_dir, basename, query=None, color=None):
		subreddit = query
		if subreddit == None:
			subreddit = self._subreddit_list[randint(0, len(self._subreddit_list)-1)].strip()
		log.info('chosen subreddit: %s'%subreddit)

		reddit = praw.Reddit(user_agent=Const.app_name)
		posts = reddit.get_subreddit(subreddit).get_hot(limit=posts_limit)

		urls = [p.url for p in posts]
		retries = 3
		while retries > 0:
			try:
				url = urls[randint(0, len(urls) - 1)]
				ext = url[url.rfind('.')+1:]

				log.info('url: ' + url + ', extension: ' + ext)

				if ext not in Const.image_extensions:
					if url.find('imgur') != -1:
						imgur = Imgur()
						url = imgur.get_image_url_from_page(url)
						ext = url[url.rfind('.')+1:]
					else:
						log.debug('not a direct link to image')
						raise ServiceException()
				retries = 0
			except ServiceException:
				retries -= 1

		save_filepath = joinpath(pictures_dir, basename) + '.' + ext

		with web.download(url, save_filepath, eh=True) as d:
			d.start()

		return basename + '.' + ext


if config.get(Reddit.name, 'enabled', default=True, type=bool):
	service_factory.add(Reddit.name, Reddit)
