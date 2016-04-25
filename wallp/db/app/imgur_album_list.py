
from .itemlist import ItemList
from ..model.imgur_album import ImgurAlbum


class ImgurAlbumListError(Exception):
	pass


class ImgurAlbumList(ItemList):
	item_name	= 'imgur album'
	table		= ImgurAlbum
	item_col	= 'album_id'
	exc_cls		= ImgurAlbumListError

