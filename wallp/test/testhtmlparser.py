import sys

from wallp.htmlparser import HtmlParser, DebugDump


if __name__ == '__main__':
	dd = DebugDump(debug=False, filter=[('class', 'left main')])
	parser = HtmlParser(skip_tags=['head'], ddump=dd)

	arg = sys.argv[1]
	if arg.startswith('http'):
		import wallp.web as web
		data = web.download(arg)
		parser.feed(data)
	else:
		with open(sys.argv[1], 'r') as f:
			parser.feed(f.read())

	etree = parser.etree
	print((etree.tag))

	if arg.find('/a/') != -1:
		image_divs = etree.findall('.//div[@class=\'left main\']/div[@class=\'panel\']'
						'/div[@id=\'image-container\']//div[@class=\'image\']')
	else:
		image_divs = etree.findall('.//div[@class=\'left main-image\']/div[@class=\'panel\']'
						'/div[@id=\'image\']//div[@class=\'image textbox\']')

	print(('image_divs:', len(image_divs)))
