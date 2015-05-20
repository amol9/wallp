
from twisted.internet.protocol import Factory	#temp import
from .wallp_server import WallpServer


WallpServerFactory = Factory.forProtocol(WallpServer)

