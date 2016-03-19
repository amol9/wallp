from unittest import TestCase, main as ut_main

from wallp.service.reddit import Reddit, RedditError


class TestReddit(TestCase):

	def test_get_imgur_image_id(self):
		valid_id_urls = ['http://imgur.com/1234567',
				'http://imgur.com/1abcdef',
				'http://imgur.com/e3er43d/',
				'http://imgur.com/1234567/?']

		invalid_id_urls = ['http://imgur.com/123456',
				'http://imgur.com/123456',
				'http://imgur.com/12345678']
	

		reddit = Reddit()

		for url in valid_id_urls:
			self.assertEquals(len(reddit.get_imgur_image_id(url)), 7)

		for url in invalid_id_urls:
			self.assertRaises(RedditError, reddit.get_imgur_image_id, url)


if __name__ == '__main__':
	ut_main()

