#source: https://code.google.com/p/bfg-pages/source/browse/trunk/pages/getimageinfo.py

from wallp.system import *
if is_py3():
	from io import BytesIO
else:
	import BytesIO
import struct


def get_image_info(data):
	#data = str(data)
	size = len(data)
	height = -1
	width = -1
	content_type = ''

	# handle GIFs
	if (size >= 10) and data[:6] in (b'GIF87a', b'GIF89a'):
		# Check to see if content_type is correct
		content_type = 'image/gif'
		w, h = struct.unpack("<HH", data[6:10])
		width = int(w)
		height = int(h)

	# See PNG 2. Edition spec (http://www.w3.org/TR/PNG/)
	# Bytes 0-7 are below, 4-byte chunk length, then 'IHDR'
	# and finally the 4-byte width, height
	elif ((size >= 24) and data.startswith(b'\211PNG\r\n\032\n') and (data[12:16] == b'IHDR')):
		content_type = 'image/png'
		w, h = struct.unpack(">LL", data[16:24])
		width = int(w)
		height = int(h)

	# Maybe this is for an older PNG version.
	elif (size >= 16) and data.startswith(b'\211PNG\r\n\032\n'):
		# Check to see if we have the right content type
		content_type = 'image/png'
		w, h = struct.unpack(">LL", data[8:16])
		width = int(w)
		height = int(h)

	# handle JPEGs
	elif (size >= 2) and data.startswith(b'\377\330'):
		content_type = 'image/jpeg'
		jpeg = BytesIO(data)
		jpeg.read(2)
		b = jpeg.read(1)
		try:
			while (b and ord(b) != 0xDA):
				while (ord(b) != 0xFF): b = jpeg.read(1)
				while (ord(b) == 0xFF): b = jpeg.read(1)
				if (ord(b) >= 0xC0 and ord(b) <= 0xC3):
					jpeg.read(3)
					h, w = struct.unpack(">HH", jpeg.read(4))
					break
				else:
					jpeg.read(int(struct.unpack(">H", jpeg.read(2))[0])-2)
				b = jpeg.read(1)
			width = int(w)
			height = int(h)
		except struct.error:
			pass
		except ValueError:
			pass

	# handle bmps
	elif (size >= 54) and data.startswith(b'BM'):
		content_type = 'image/bmp'
		w, h = struct.unpack('ii', data[18:26])
		width = int(w)
		height = int(h)

	return content_type, width, height

