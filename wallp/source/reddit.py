from random import randint
from os.path import join as joinpath
import re

import praw
from requests.exceptions import HTTPError
from giraf.api import Imgur as GImgur, ImgurError as GImgurError

from ..util import log, Retry
from ..globals import Const
from ..db import SubredditList, Config
from .image_context import ImageContext
from .base import SourceError, SourceParams
from .base_source import BaseSource


class RedditParams(SourceParams):
	name = 'reddit'

	def __init__(self, query=None, subreddit=None, limit=10):
		self.query	= query
		self.subreddit	= subreddit
		self.limit	= limit


class RedditError(Exception):
	pass


class Reddit(BaseSource):
	name = 'reddit'

	def __init__(self):
		super(Reddit, self).__init__()
		self._posts_limit = Config().get('reddit.posts_limit')
		self._imgur = GImgur()


	def get_image(self, params=None):
		if self.image_urls_available():
			return self.http_get_image_to_temp_file()

		if params.query is None and params.subreddit is None:
			params.subreddit = SubredditList().get_random()
			self.add_trace_step('random subreddit', subreddit)

		self._params = params
		self.search()
		return self.http_get_image_to_temp_file()


	def search(self):
		posts = self.get_posts()

		for p in posts:
			url = p.url
			url = url[url.rfind('?') + 1 : ]
			ext = url[url.rfind('.') + 1 : ]

			if ext in Const.image_extensions:
				self.add_url(p.url, ImageContext(artist=p.author.name, title=p.title, url=p.permalink))


	def old_logic(self):
		query = None
		subreddit = None

		posts = self.get_posts()
		for p in posts:
			self.add_url(p.url, ImageContext(artist=p.author.name, title=p.title, url=p.permalink))

		retry = Retry(retries=self.image_count, final_exc=ServiceError())
		log.debug('%d posts found'%self.image_count)

		while retry.left():
			url = self.select_url(add_trace_step=False)
			ext = url[url.rfind('.') + 1 : ]

			if ext not in Const.image_extensions:
				if url.find('imgur.com') != -1:
					try:
						url = self.get_imgur_image_url(url)
					except RedditError as e:
						log.debug(str(e))
						continue
					retry.cancel()
				else:
					log.debug('not a direct link to image')
					retry.retry()
			else:
				self.add_trace_step('selected url', url)
				retry.cancel()

		return url


	def get_imgur_image_id(self, post_url):
		image_id_regex = re.compile(".*/([a-zA-Z0-9]{7})([^a-zA-Z0-9].*|$)")

		match = image_id_regex.match(post_url)
		if match is None:
			raise RedditError('not a valid imgur post url')

		image_id = match.group(1)
		return image_id
		

	def get_imgur_image_url(self, post_url):
		image_id = self.get_imgur_image_id(post_url)

		try:
			i = self._imgur.get_image(image_id)
			return i.link
		except (GImgurError, AttributeError) as e:
			raise RedditError(str(e))


	def get_posts(self):
		p = self._params
		query, subreddit, limit = p.query, p.subreddit, p.limit

		reddit = praw.Reddit(user_agent=Const.app_name, timeout=Config().get('http.timeout'))

		try:
			if subreddit is None:
				if query is None:
					raise ServiceError('no subreddit and no query, not cool')
				posts = reddit.search(query)
			else:
				sub = reddit.get_subreddit(subreddit)
				if query is None:
					posts = sub.get_hot(limit=limit)
				else:
					posts = sub.search(query)
		except HTTPError as e:
			log.error(e)
			printer.printf('error', str(e))
			raise ServiceError()
		
		return posts

