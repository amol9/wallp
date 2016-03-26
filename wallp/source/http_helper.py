
from redlib.api.misc import Retry
from redlib.api.image import get_image_info

from .base import SourceError
from ..web.func import get, HttpError, exists
from ..db.config import Config
from ..util.logger import log
from ..util.printer import printer


class HttpHelper:
	
	def __init__(self):
		pass


	def get(self, url, msg=None, headers=None):
		try:
			return get(url, msg=msg, headers=headers)
		except HttpError as e:
			log.error(e)
			raise SourceError(str(e))


	def download_image(self, images, trace):	
		retry = Retry(retries=3, exp_bkf=False, final_exc=SourceError('could not get image from source'))

		while retry.left():
			try:
				image = images.select()
				printer.printf('random url', image.url)
				
				if image.url is None:
					continue

				temp_filepath = get(image_url, msg='getting image', max_content_length=Config().get('image.max_size'),
						save_to_temp_file=True)

				image.type, image.i_width, r.i_height = self.get_image_info(temp_filepath)

				if image.ext is None:
					image.ext = image.url[image_url.rfind('.') + 1 : ]

				image.temp_filepath = temp_filepath
				trace.add_step('random url', image.url)

				retry.cancel()

			except (HttpError, ImageError) as e:
				log.error(e)
				printer.printf('error', str(e))
				retry.retry()

		return image


