from wallp.system import *
if is_py3():
	from html.parser import HTMLParser
else:	
	from HTMLParser import HTMLParser
from xml.etree.ElementTree import XMLParser, Element, SubElement, ElementTree
import re
import sys


class DebugDump():
	def __init__(self, debug=False, filter=None, children=True):
		self._debug = debug
		self._filter = filter
		self._start_level = None

	
	def dump_tag(self, tag, attrs=None, end=False, level=0, msg=None):
		if self._debug:
			if self._filter and self._start_level is None:
				matches = [(k, v) for (k, v) in self._filter if (k, v) in attrs] if attrs else []
				#print matches
				if len(matches) == 0:
					return
				self._start_level = level

			if self._start_level is not None:
				if end:
					if level == self._start_level:
						self._start_level = None
			
			spaces = ''.join([' ' for i in range(level)])
			attr_string = None
			if attrs:
				attr_string = ''
				for (k, v) in attrs:
					attr_string += ' ' + str(k) + '=\"' + str(v) + '\"'
			print(('%s<%s%s%s>%s'%(spaces, ('/' if end else ''), tag, (attr_string if attr_string else ''),
						(' ' + msg if msg else ''))))
		

class HtmlParser(HTMLParser):
	def __init__(self, skip_tags=[], ddump=None):
		self._root = None
		self._stack = []
		self._skip_tags = skip_tags
		self._skip = False, None
		self._ddump = ddump

		HTMLParser.__init__(self, convert_charrefs=True)

	
	def handle_starttag(self, tag, attrs):
		if self._skip[0] == True:
			return
		if tag in self._skip_tags:
			self._skip = True, tag
			return

		if self._ddump: self._ddump.dump_tag(tag, attrs, level=len(self._stack))

		attr_dict = dict((k, v) for (k, v) in attrs)
		if self._root == None:
			self._root = Element(tag, attr_dict)
			self._stack.append(self._root)
		else:
			e = SubElement(self._stack[-1], tag, attr_dict)
			self._stack.append(e)


	def handle_endtag(self, tag):
		if self._skip[0] == True:
			if tag == self._skip[1]:
				self._skip = False, None
			return
		
		if tag == self._stack[-1].tag or True:
			self._stack.pop()
		else:
			if self._ddump:
				m = self._stack[-1]
				attrs = [(k, v) for (k, v) in list(m.attrib.items())]
				self._ddump.dump_tag(m.tag, attrs=attrs, level=len(self._stack), msg='mismatch')

		if self._ddump: self._ddump.dump_tag(tag, end=True, level=len(self._stack))


	def handle_data(self, data):
		if self._skip[0]:
			return

		if self._stack:
			if self._stack[-1].text:
				self._stack[-1].text += data
			else:
				self._stack[-1].text = data

	
	def get_element_tree(self):
		return self._root


	etree = property(get_element_tree)


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

	#import pdb; pdb.set_trace()
	print(('image_divs:', len(image_divs)))
