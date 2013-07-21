#    Copyright (c) 2012 Connor Sherson
#
#    This file is part of ThisHackishMess
#
#    ThisHackishMess is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
