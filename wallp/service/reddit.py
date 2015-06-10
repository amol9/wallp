from random import randint
from os.path import join as joinpath
from zope.interface import implementer

from ..util import log, Retry
from .imgur import Imgur
from ..globals import Const
from .service import IHttpService, ServiceError
from .image_source import ImageSource
from ..db import SubredditList, Config, ImageTrace
from .image_mixin import ImageMixin
from ..web import func as webfunc


@implementer(IHttpService)
class Reddit(ImageMixin):
	name = 'reddit'

	def __init__(self):
		#self._subreddit_list = config.get_list('reddit', 'subreddit_list', default=subreddit_list)
		super(Reddit, self).__init__()
		self._posts_limit = Config().get('reddit.posts_limit')


	def get_image_url(self, query=None, color=None):
		subreddit = query
		if subreddit == None:
			subreddit = SubredditList().get_random()
		log.info('chosen subreddit: %s'%subreddit)

		urls = webfunc.get_subreddit_post_urls(subreddit, limit=self._posts_limit)
		retry = Retry(retries=3, final_exc=ServiceError())

		while retry.left():
			url = urls[randint(0, len(urls) - 1)]
			ext = url[url.rfind('.')+1:]

			log.info('url: ' + url + ', extension: ' + ext)

			if ext not in Const.image_extensions:
				if url.find('imgurxx.com') != -1:
					imgur = Imgur()
					url = imgur.get_image_url_from_page(url)
					#ext = url[url.rfind('.')+1:]
					retry.cancel()
				else:
					log.debug('not a direct link to image')
					retry.retry()
			else:
				retry.cancel()

		#save_filepath = joinpath(pictures_dir, basename) + '.' + ext

		#download(url, save_filepath)

		return url

