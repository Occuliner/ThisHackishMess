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
    self.temporaryEvents = {'preTick':[], 'postTick':[], 'preNetworkEvent':[], 
                            'postNetworkEvent':[], 'onLoad':[], 'onLaunch':[]}
    def __init__( self, playState ):
        self.playStateRef = weakref.ref( playState )

    def callMethod( self, strTuple ):
        if not hasattr( strTuple[0] ):
            print "GameLogicManager has been told to call a method that doesn't exist:", strTuple[0]
        getattr( self, strTuple[0] )( *strTuple[1], **strTuple[2] )

    def callEvents( self, callList ):
        for eachCall in callList:
            callMethod( eachCall )

    def performTempEvents( self, string ):
        callEvents( self.temporaryEvents[string] )
        self.temporaryEvents[string] = []

    def preTick( self, dt ):
        performTempEvents( 'preTick' )

    def postTick( self, dt ):
        performTempEvents( 'postTick' )

    def preNetworkEvent( self ):
        performTempEvents( 'preNetworkTick' )

    def postNetworkEvent( self ):
        performTempEvents( 'postNetworkTick' )

    def onLoad( self ):
        performTempEvents( 'onLoad' )

    def onLaunch( self ):
        performTempEvents( 'onLaunch' )
