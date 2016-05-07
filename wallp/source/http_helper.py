
from redlib.api.misc import Retry
from redlib.api.image import get_image_info
from PIL import Image

from .base import SourceError
from ..web.func import get, HttpError, exists
from ..db.app.config import Config
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


	def download_image(self, images, trace, headers=None):	
		retry = Retry(retries=3, exp_bkf=False, final_exc=SourceError('could not get image from source'))

		while retry.left():
			try:
				image = images.select()
				
				if image.url is None:
					continue

				temp_filepath = get(image.url, msg='getting image', max_content_length=Config().get('image.max_size'),
						save_to_temp_file=True, headers=headers)

				im = Image.open(temp_filepath)
				image.type = im.format.lower()
				image.i_width, image.i_height = im.size
				im.close()

				if image.i_width < 1 or image.i_height < 1:
					retry.retry()
					continue

				if image.ext is None:
					image.ext = image.url[image.url.rfind('.') + 1 : ]

				image.temp_filepath = temp_filepath

				retry.cancel()

			except (HttpError, IOError) as e:
				log.error(e)
				printer.printf('error', str(e))
				retry.retry()

		return image


