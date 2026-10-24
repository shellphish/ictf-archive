import irclib

irclib.DEBUG=False

class IrcBot(object):

    # Public messages
    def handlePubMessage (self, connection, event):
        if event.target() == self.source_channel:
            #print event.target() + '> ' + event.source().split ( '!' ) [ 0 ] +': ' + event.arguments() [ 0 ]
            self.server.privmsg(self.dest_channel, event.arguments()[0])

    # Private messages
    def handlePrivMessage (self, connection, event):
        connection.privmsg ( event.source().split ( '!' ) [ 0 ], "Hello, cutie. Nothing to see here.")


    def __init__(self,
                 network,
                 port,
                 nick,
                 source_channel,
                 dest_channel):
        self.source_channel = source_channel
        self.dest_channel = dest_channel
        irc = irclib.IRC()
        self.server = irc.server()
        self.server.connect (network, port, nick, ircname = nick)
        self.server.join (source_channel)
        self.server.join(dest_channel)
        irc.add_global_handler ('pubmsg', self.handlePubMessage)
        irc.add_global_handler ('privmsg', self.handlePrivMessage)
        irc.process_forever()

IrcBot('irc.ictf2011.info', 6667, 'Bottana', dest_channel='#egoats',
        source_channel='#egoats_CanIHazSecretRoomz')
