from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from .dbsession import DBSession

from .imgur_album import ImgurAlbum
from .subreddit import Subreddit
from .image_trace import ImageTrace
from .image import Image
from .search_term import SearchTerm
from .setting import Setting
from .var import Var

from .config import Config, ConfigError
from .globalvars import GlobalVars, VarError

from .itemlist import ItemList, ImgurAlbumList, SubredditList, SearchTermList, NotFoundError
from .exc import *

print('dev wallp db init')
