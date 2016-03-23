
from redlib.api.misc import Retry

from .source import Source, SourceResponse, SourceError
from ..service.image_info_mixin import ImageInfoMixin
from ..service.image_urls_mixin import ImageUrlsMixin
from ..web.func import get, HttpError
from ..db.config import Config
from ..util.logger import log
from ..util.printer import printer


class BaseSource(Source, ImageInfoMixin, ImageUrlsMixin):
	
	def __init__(self):
		ImageInfoMixin.__init__(self)
		ImageUrlsMixin.__init__(self)

		self._response = SourceResponse()


	def http_get(self, url, msg=None, headers=None):
		try:
			return get(url, msg=msg, headers=headers)
		except HttpError as e:
			log.error(e)
			raise SourceError(str(e))


	def http_get_image_to_temp_file(self):	
		retry = Retry(retries=3, final_exc=SourceError('could not get image from source'))

		while retry.left():
			try:
				image_url = self.select_url()
				
				if image_url is None:
					raise SourceError('no image url')

				ext = image_url[image_url.rfind('.') + 1 : ]

				temp_image_path = get(image_url, msg='getting image', max_content_length=Config().get('image.max_size'),
						save_to_temp_file=True)

				print 'temp path', temp_image_path
				retry.cancel()

			except HttpError as e:
				log.error(e)
				printer.printf('error', str(e))
				retry.retry()

		self._response.url 		= image_url
		self._response.temp_filepath 	= temp_image_path
		self._response.ext 		= ext





