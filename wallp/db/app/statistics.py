from datetime import timedelta
from time import time

from sqlalchemy import func
from redlib.api.net import AbsUrl

from ..model.image import Image
from ..dbsession import DBSession


class Statistics:

	def __init__(self):
		self._db_session = DBSession()

		self.create()


	def create(self):
		dbs = self._db_session
		self.wallpaper_count = dbs.query(Image).count()

		all_image_urls = dbs.query(Image).filter(Image.url != None).distinct(Image.url).with_entities(Image.url)
		all_domains = list(map(lambda t : AbsUrl(t[0]).domain, all_image_urls))
	
		domain_freq = self.freq_list(all_domains)
		self.top_domains = domain_freq[0 : 10]

		self.avg_downloaded_image_size = dbs.query(func.avg(Image.size)).filter(Image.url != None).scalar() or 0
	
		first_image = dbs.query(Image).first()
		usage_time = timedelta(seconds=int(time() - (first_image and first_image.time or int(time()))))
		self.usage_time = usage_time

		self.avg_wallpaper_life = self.usage_time and str(self.usage_time / self.wallpaper_count).split('.')[0] or '0:00:00'


	def freq_list(self, list, desc=True): 
		freq_list = []
		for i in range(0, len(list)):
			d = list[i]
			if d is not None:
				c = 1
				for j in range(i + 1, len(list)):
					if d == list[j]:
						c += 1
						list[j] = None

				k = 0
				for _ in range(0, len(freq_list)):
					if freq_list[k][1] < c:
						break
					k += 1

				freq_list.insert(k, (d, c))

		return freq_list


	def freq_list2(self):
		'''
		uniq_domains = list(set(all_domains))
		domain_count = []

		for d in uniq_domains:
			domain_count.append((d, all_domains.count(d)))
		
		sorted_domain_count = sorted(domain_count, key=lambda i : i[1], reverse=True)'''


