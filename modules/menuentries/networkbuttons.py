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
            #self.parentState.menu.playState.connectToGame()
            print "Button disabled until I can be bothered making a proper connect dialog for it."
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
