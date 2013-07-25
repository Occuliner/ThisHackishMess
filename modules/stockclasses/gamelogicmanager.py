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
    def __init__( self, playState ):
        self.playStateRef = weakref.ref( playState )

    def callMethod( self, callTuple ):
        if not hasattr( callTuple[0] ):
            print "GameLogicManager has been told to call a method that doesn't exist:", callTuple[0]
        getattr( self, callTuple[0] )( *callTuple[1], **callTuple[2] )

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
