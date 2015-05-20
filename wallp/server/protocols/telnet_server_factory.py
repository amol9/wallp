
from twisted.internet.protocol import Factory	#temp import
from .telnet_server import TelnetServer


TelnetServerFactory = Factory.forProtocol(TelnetServer)

