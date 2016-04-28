from random import randint
from os.path import join as joinpath
import re

import praw
from praw.errors import InvalidSubreddit, NotFound
from requests.exceptions import HTTPError, ConnectionError
from giraf.api import Imgur as GImgur, ImgurError as GImgurError

from ..util import log, Retry
from .. import const
from ..db.app.subreddit_list import SubredditList
from .base import SourceError, SourceParams, Source
from .image import Image
from .images import Images
from .http_helper import HttpHelper
from .trace import Trace
from ..db.app.config import Config


class RedditParams(SourceParams):
	name = 'reddit'

	def __init__(self, query=None, subreddit=None, limit=None):
		self.query	= query
		self.subreddit	= subreddit
		self.limit	= limit

		self.hash_params = ['query', 'subreddit', 'limit']


class RedditError(Exception):
	pass


class Reddit(Source):
	name = 'reddit'
	params_cls = RedditParams

	def __init__(self):
		super(Reddit, self).__init__()

		self._config = Config(group=self.name)
		self._imgur = None

		self._trace 	= Trace()
		self._http 	= HttpHelper()
	

	def get_imgur(self):
		if self._imgur is None:
			self._imgur = GImgur()
		return self._imgur


	def get_image(self, params=None):
		params = params or RedditParams()
		params.limit = params.limit or self._config.pget('posts_limit')

		cache = True
		if params.query is None and params.subreddit is None:
			params.subreddit = SubredditList().random()
			self._trace.add_step('random subreddit', params.subreddit)
			cache = False

		self._images = Images(params, cache=cache, cache_timeout='1h', trace=self._trace)

		if not self._images.available():
			self._params = params
			self.exc_call(self.search)

		return self._http.download_image(self._images, self._trace)


	def search(self):
		posts = self.get_posts()

		for p in posts:
			get = lambda i : getattr(p, i, None)

			url = get('url')
			if url is None:
				continue

			url = url[url.rfind('?') + 1 : ]
			ext = url[url.rfind('.') + 1 : ]

			if ext in const.image_extensions:
				get_user = lambda : get('author') and getattr(get('author'), 'name', None)
				image = Image(url=get('url'), user=get_user(), title=get('title'), context_url=get('permalink'))
				self._images.add(image)


	'''def old_logic(self):
		query = None
		subreddit = None

		posts = self.get_posts()
		for p in posts:
			self.add_url(p.url, ImageContext(artist=p.author.name, title=p.title, url=p.permalink))

		retry = Retry(retries=self.image_count, final_exc=ServiceError())
		log.debug('%d posts found'%self.image_count)

		while retry.left():
			url = self.select_url(_trace.add_step=False)
			ext = url[url.rfind('.') + 1 : ]

			if ext not in const.image_extensions:
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
				self._trace.add_step('selected url', url)
				retry.cancel()

		return url'''


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
			i = self.get_imgur().get_image(image_id)
			return i.link
		except (GImgurError, AttributeError) as e:
			raise RedditError(str(e))


	def get_posts(self):
		p = self._params
		query, subreddit, limit = p.query, p.subreddit, p.limit

		reddit = praw.Reddit(user_agent=const.app_name, timeout=self._config.get('http.timeout'), disable_update_check=True)

		if subreddit is None:
			if query is None:
				raise ServiceError('no subreddit and no query, not cool')
			posts = self.exc_call(reddit.search, query)
		else:
			sub = self.exc_call(reddit.get_subreddit, subreddit)
			if query is None:
				posts = self.exc_call(sub.get_hot, limit=limit)
			else:
				posts = self.exc_call(sub.search, query)
	
		return posts


	def exc_call(self, method, *args, **kwargs):
		try:
			return method(*args, **kwargs)

		except (HTTPError, ConnectionError, InvalidSubreddit, NotFound) as e:
			msg = 'invalid subreddit' if type(e) == InvalidSubreddit else str(e)
			log.error(msg)
			raise SourceError(msg)

	def get_trace(self):
		return self._trace.steps

