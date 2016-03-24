
from redlib.api.misc import Retry
from redlib.api.image import get_image_info

from .base import Source, SourceResponse, SourceError
from .image_info_mixin import ImageInfoMixin
from .image_urls_mixin import ImageUrlsMixin
from ..web.func import get, HttpError
from ..db.config import Config
from ..util.logger import log
from ..util.printer import printer
from .config_mixin import ConfigMixin


class ImageError(Exception):
	pass


class BaseSource(Source, ImageInfoMixin, ImageUrlsMixin, ConfigMixin):
	
	def __init__(self):
		ImageInfoMixin.__init__(self)
		ImageUrlsMixin.__init__(self)
		ConfigMixin.__init__(self)

		self._response = SourceResponse()


	def http_get(self, url, msg=None, headers=None):
		try:
			return get(url, msg=msg, headers=headers)
		except HttpError as e:
			log.error(e)
			raise SourceError(str(e))


	def http_get_image_to_temp_file(self):	
		retry = Retry(retries=3, exp_bkf=False, final_exc=SourceError('could not get image from source'))
		r = self._response

		while retry.left():
			try:
				image_url = self.select_url()
				
				if image_url is None:
					raise SourceError('no image url')

				temp_filepath = get(image_url, msg='getting image', max_content_length=Config().get('image.max_size'),
						save_to_temp_file=True)

				r.im_type, r.im_width, r.im_height = self.get_image_info(temp_filepath)

				ext = image_url[image_url.rfind('.') + 1 : ]
				r.url, r.temp_filepath, r.ext = image_url, temp_filepath, ext

				retry.cancel()

			except (HttpError, ImageError) as e:
				log.error(e)
				printer.printf('error', str(e))
				retry.retry()

		return r


	def get_image_info(self, filepath):
		im_type, im_width, im_height = get_image_info(None, filepath=filepath)

		if im_width < 1 or im_height < 1:
			raise ImageError('bad image data')
	
		return im_type, im_width, im_height

