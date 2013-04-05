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

from button import Button
from imageload import loadImage

class ConnectToButton( Button ):
    image = loadImage( "connectbutton.png", 2 )
    rect = image.get_rect()
    rect.topleft = ( 24, 164 )
    def __init__( self, menu=None ):
        Button.__init__( self, None, None, menu )

    def push( self, clickKey, click ):
        if "up" in clickKey:
            self.parentState.menu.playState.connectToGame()
            #aBoundEditState = SensorEditState( self.parentState.menu )
            #self.parentState.menu.loadMenuState( aBoundEditState )

class HostButton( Button ):
    image = loadImage( "hostbutton.png", 2 )
    rect = image.get_rect()
    rect.topleft = ( 24, 184 )
    def __init__( self, menu=None ):
        Button.__init__( self, None, None, menu )

    def push( self, clickKey, click ):
        if "up" in clickKey:
            self.parentState.menu.playState.hostGame()
            #aBoundEditState = SensorEditState( self.parentState.menu )
            #self.parentState.menu.loadMenuState( aBoundEditState )
