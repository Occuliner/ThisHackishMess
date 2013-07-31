# Copyright (c) 2013 Connor Sherson
#
# This software is provided 'as-is', without any express or implied
# warranty. In no event will the authors be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
#    1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
#
#    2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
#
#    3. This notice may not be removed or altered from any source
#    distribution.

import weakref

class GameLogicManager:
    """The GameLogicManager is a class to handle game-specific events within the main loop,
    on network events, etc."""
    temporaryEvents = {'preTick':[], 'postTick':[], 'preNetworkTick':[], 
                            'postNetworkTick':[], 'onLoad':[], 'onLaunch':[]}
    allowedClientMethods = []
    def __init__( self, playState ):
        self.playStateRef = weakref.ref( playState )

    def joinGame( self, clientInfo ):
        #This occurs on the host-end when a client sends the join game message.
        #This can vary HUGELY.
        #The idea is that you should probably create a player instance here.
        #Below is a template for this method
        playState = self.playStateRef()
        if not clientInfo.isPlayer:
            classDef = playState.devMenuRef().masterEntitySet.getEntityClass("NewPlayer")
            destGroup = getattr( playState, "networkPlayers" )
            playerEntity = classDef( pos=[0,0], vel=[0,0], group=destGroup )
            playState.networkNode.players[playState.networkNode.getPlayerKey( clientInfo )] = [ playerEntity ]
            clientInfo.isPlayer = True
            clientInfo.connection.net_setPlayerEnt( playState.networkNode.networkTick, playerEntity.id )

    def exitGame( self, clientInfo ):
        #This occurs on host-end when a client disconnects.
        #Again, this can vary a lot.
        #But what you want is probably something like this:
        playState = self.playStateRef()
        if clientInfo.isPlayer:
            playerKey = playState.networkNode.getPlayerKey( clientInfo )
            playerEntList = playState.networkNode.players[playerKey]
            del playState.networkNode.players[playerKey]
            for each in playerEntList:
                if each in playState.networkPlayers:
                    each.kill()

    def callMethod( self, callTuple ):
        if not hasattr( callTuple[0] ):
            print "GameLogicManager has been told to call a method that doesn't exist:", callTuple[0]
            return None
        getattr( self, callTuple[0] )( *callTuple[1], **callTuple[2] )

    def clientCallMethod( self, client, methodName, argDict ):
        if not hasattr( methodName ):
            print "GameLogicManager has been told to call a method that doesn't exist:", methodName
            return None
        if methodName not in self.allowedClientMethods:
            print "GameLogicManager has been told to call a method that the client isn't allowed to:", methodName
            return None
        getattr( self, methodName )( client, argDict )

    def callEvents( self, callList ):
        for eachCall in callList:
            self.callMethod( eachCall )

    def performTempEvents( self, string ):
        self.callEvents( self.temporaryEvents[string] )
        self.temporaryEvents[string] = []

    def preTick( self, dt ):
        self.performTempEvents( 'preTick' )

    def postTick( self, dt ):
        self.performTempEvents( 'postTick' )

    def preNetworkTick( self, dt ):
        self.performTempEvents( 'preNetworkTick' )

    def postNetworkTick( self, dt ):
        self.performTempEvents( 'postNetworkTick' )

    def preNetworkEvent( self, message ):
        pass

    def postNetworkEvent( self, message ):
        pass

    def onLoad( self ):
        self.performTempEvents( 'onLoad' )

    def onLaunch( self ):
        self.performTempEvents( 'onLaunch' )
