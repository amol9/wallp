from random import randint
from os.path import join as joinpath
from zope.interface import implementer
import praw

from ..util import log, Retry
from .imgur import Imgur, ImgurError
from ..globals import Const
from .service import IHttpService, ServiceError
from ..db import SubredditList, Config
from .image_info_mixin import ImageInfoMixin
from .image_urls_mixin import ImageUrlsMixin
from .image_context import ImageContext
from ..web.func import exc_wrapped


@implementer(IHttpService)
class Reddit(ImageInfoMixin, ImageUrlsMixin):
	name = 'reddit'

	def __init__(self):
		super(Reddit, self).__init__()
		self._posts_limit = Config().get('reddit.posts_limit')


	def get_image_url(self, query=None, color=None):
		subreddit = None
		if query is None:
			subreddit = SubredditList().get_random()
			self.add_trace_step('subreddit', subreddit)
		else:
			self.add_trace_step('searched', query)

		posts = self.get_subreddit_posts(subreddit, limit=self._posts_limit, query=query)
		for p in posts:
			self.add_url(p.url, ImageContext(artist=p.author.name, title=p.title, url=p.permalink))

		retry = Retry(retries=self.image_count, final_exc=ServiceError())
		log.debug('%d posts found'%self.image_count)

		while retry.left():
			url = self.select_url(add_trace_step=False)
			ext = url[url.rfind('.') + 1 : ]

			if ext not in Const.image_extensions:
				if url.find('imgur.com') != -1:
					imgur = Imgur()
					try:
						url = imgur.get_image_url_from_page(url)
					except ImgurError as e:
						log.debug(str(e))
						continue
					self.add_trace_from(imgur)
					retry.cancel()
				else:
					log.debug('not a direct link to image')
					retry.retry()
			else:
				self.add_trace_step('selected url', url)
				retry.cancel()

		return url


	@exc_wrapped
	def get_subreddit_posts(self, subreddit, limit=10, query=None):
		reddit = praw.Reddit(user_agent=Const.app_name, timeout=Const.page_timeout)

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
		
		return posts

