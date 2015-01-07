import sys

from wallp.manager import Manager

#entry point
def main():
	site = None
	query = None

	if len(sys.argv) > 1:
		if sys.argv[1] == 'debug':
			Const.debug = True
		else:
			site = sys.argv[1]
			if len(sys.argv) > 2: query = sys.argv[2]			

	mgr = Manager()
	mgr.get_image(site=site, choice=query)
	#mgr.set_image_as_desktop_back()

main()

