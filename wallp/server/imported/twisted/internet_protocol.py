# -*- test-case-name: twisted.test.test_factories,twisted.internet.test.test_protocol -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Standard implementations of Twisted protocol-related interfaces.

Start here if you are looking to write a new protocol implementation for
Twisted.  The Protocol class contains some introductory material.
"""

#from __future__ import division, absolute_import

#import random
from zope.interface import implementer

#from twisted.python import log, failure, components
#from twisted.internet import interfaces, error, defer

from . import internet_interfaces as interfaces


@implementer(interfaces.IProtocolFactory, interfaces.ILoggingContext)
class Factory:
    """
    This is a factory which produces protocols.

    By default, buildProtocol will create a protocol of the class given in
    self.protocol.
    """

    # put a subclass of Protocol here:
    protocol = None

    numPorts = 0
    noisy = True

    @classmethod
    def forProtocol(cls, protocol, *args, **kwargs):
        """
        Create a factory for the given protocol.

        It sets the C{protocol} attribute and returns the constructed factory
        instance.

        @param protocol: A L{Protocol} subclass

        @param args: Positional arguments for the factory.

        @param kwargs: Keyword arguments for the factory.

        @return: A L{Factory} instance wired up to C{protocol}.
        """
        factory = cls(*args, **kwargs)
        factory.protocol = protocol
        return factory


    def logPrefix(self):
        """
        Describe this factory for log messages.
        """
        return self.__class__.__name__


    def doStart(self):
        """Make sure startFactory is called.

        Users should not call this function themselves!
        """
        if not self.numPorts:
            if self.noisy:
                log.msg("Starting factory %r" % self)
            self.startFactory()
        self.numPorts = self.numPorts + 1

    def doStop(self):
        """Make sure stopFactory is called.

        Users should not call this function themselves!
        """
        if self.numPorts == 0:
            # this shouldn't happen, but does sometimes and this is better
            # than blowing up in assert as we did previously.
            return
        self.numPorts = self.numPorts - 1
        if not self.numPorts:
            if self.noisy:
                log.msg("Stopping factory %r" % self)
            self.stopFactory()

    def startFactory(self):
        """This will be called before I begin listening on a Port or Connector.

        It will only be called once, even if the factory is connected
        to multiple ports.

        This can be used to perform 'unserialization' tasks that
        are best put off until things are actually running, such
        as connecting to a database, opening files, etcetera.
        """

    def stopFactory(self):
        """This will be called before I stop listening on all Ports/Connectors.

        This can be overridden to perform 'shutdown' tasks such as disconnecting
        database connections, closing files, etc.

        It will be called, for example, before an application shuts down,
        if it was connected to a port. User code should not call this function
        directly.
        """

    def buildProtocol(self, addr):
        """Create an instance of a subclass of Protocol.

        The returned instance will handle input on an incoming server
        connection, and an attribute \"factory\" pointing to the creating
        factory.

        Override this method to alter how Protocol instances get created.

        @param addr: an object implementing L{twisted.internet.interfaces.IAddress}
        """
        p = self.protocol()
        p.factory = self
        return p


class BaseProtocol:
    """
    This is the abstract superclass of all protocols.

    Some methods have helpful default implementations here so that they can
    easily be shared, but otherwise the direct subclasses of this class are more
    interesting, L{Protocol} and L{ProcessProtocol}.
    """
    connected = 0
    transport = None

    def makeConnection(self, transport):
        """Make a connection to a transport and a server.

        This sets the 'transport' attribute of this Protocol, and calls the
        connectionMade() callback.
        """
        self.connected = 1
        self.transport = transport
        self.connectionMade()

    def connectionMade(self):
        """Called when a connection is made.

        This may be considered the initializer of the protocol, because
        it is called when the connection is completed.  For clients,
        this is called once the connection to the server has been
        established; for servers, this is called after an accept() call
        stops blocking and a socket has been received.  If you need to
        send any greeting or initial message, do it here.
        """

#connectionDone=failure.Failure(error.ConnectionDone())
#connectionDone.cleanFailure()
connectionDone = None


@implementer(interfaces.IProtocol, interfaces.ILoggingContext)
class Protocol(BaseProtocol):
    """
    This is the base class for streaming connection-oriented protocols.

    If you are going to write a new connection-oriented protocol for Twisted,
    start here.  Any protocol implementation, either client or server, should
    be a subclass of this class.

    The API is quite simple.  Implement L{dataReceived} to handle both
    event-based and synchronous input; output can be sent through the
    'transport' attribute, which is to be an instance that implements
    L{twisted.internet.interfaces.ITransport}.  Override C{connectionLost} to be
    notified when the connection ends.

    Some subclasses exist already to help you write common types of protocols:
    see the L{twisted.protocols.basic} module for a few of them.
    """

    def logPrefix(self):
        """
        Return a prefix matching the class name, to identify log messages
        related to this protocol instance.
        """
        return self.__class__.__name__


    def dataReceived(self, data):
        """Called whenever data is received.

        Use this method to translate to a higher-level message.  Usually, some
        callback will be made upon the receipt of each complete protocol
        message.

        @param data: a string of indeterminate length.  Please keep in mind
            that you will probably need to buffer some data, as partial
            (or multiple) protocol messages may be received!  I recommend
            that unit tests for protocols call through to this method with
            differing chunk sizes, down to one byte at a time.
        """

    def connectionLost(self, reason=connectionDone):
        """Called when the connection is shut down.

        Clear any circular references here, and any external references
        to this Protocol.  The connection has been closed.

        @type reason: L{twisted.python.failure.Failure}
        """



