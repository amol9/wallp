from random import randint
from os.path import join as joinpath
from zope.interface import implementer

from ..util import log, Retry
from .imgur import Imgur
from ..globals import Const
from .service import IHttpService, ServiceError
from ..db import SubredditList, Config
from .image_info_mixin import ImageInfoMixin
from .image_urls_mixin import ImageUrlsMixin
from ..web import func as webfunc


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

		urls = webfunc.get_subreddit_post_urls(subreddit, limit=self._posts_limit, query=query)
		self.add_urls(urls)
		retry = Retry(retries=len(urls), final_exc=ServiceError())

		log.debug('%d posts found'%len(urls))
		while retry.left():
			url = self.select_url()
			ext = url[url.rfind('.') + 1 : ]

			if ext not in Const.image_extensions:
				if url.find('imgur.com') != -1:
					imgur = Imgur()
					url = imgur.get_image_url_from_page(url)
					self.add_trace_from(imgur)
					retry.cancel()
				else:
					log.debug('not a direct link to image')
					retry.retry()
			else:
				retry.cancel()

		self.add_trace_step('selected url', url)
		return url

