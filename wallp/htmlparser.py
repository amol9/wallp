from xml.etree.ElementTree import XMLParser, Element, SubElement, ElementTree
import re
import sys
from HTMLParser import HTMLParser


class HtmlParser(HTMLParser):
	def __init__(self, skip_tags=[]):
		self._root = None
		self._stack = []
		self._skip_tags = skip_tags
		self._skip = False, None
		HTMLParser.__init__(self)

	
	def handle_starttag(self, tag, attrs):
		#print 'start: %s'%tag
		if tag in self._skip_tags:
			self._skip = True, tag
			return

		attr_dict = dict((k, v) for (k, v) in attrs)
		if self._root == None:
			self._root = Element(tag, attr_dict)
			self._stack.append(self._root)
		else:
			e = SubElement(self._stack[-1], tag, attr_dict)
			self._stack.append(e)



	def handle_endtag(self, tag):
		#print 'end: %s'%tag
		if self._skip[0] == True:
			if tag == self._skip[1]:
				self._skip = False, None
			else:
				return
		t = ''
		#if tag == self._stack[-1].tag:
		t = self._stack.pop()
		#print 'pop: %s'%t


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
	parser = HtmlParser()
	with open(sys.argv[1], 'r') as f:
		parser.feed(f.read())
	root = parser.etree
	print root.tag
