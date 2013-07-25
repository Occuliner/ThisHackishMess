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

from imageload import loadImage

from button import Button

class PhysicsVisButton( Button ):
    image = loadImage("physicsvis.png",2)
    def __init__( self, menu=None ):
        Button.__init__( self, None, None, menu )
        self.rect = self.image.get_rect()
        self.rect.topleft = ( 30, 370 )
        self.on = False
    def push( self, clickKey, click ):
        if "up" in clickKey:
            if not self.on:
                self.on = True
                self.parentState.menu.playState.lineVisualiser.renderLines = True
                self.parentState.menu.playState.lineVisualiser.renderPhysicsLines = True
            elif self.on:
                self.on = False
                self.parentState.menu.playState.lineVisualiser.forceNoRender = True
