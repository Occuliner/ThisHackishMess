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

import pygame, os
from staticimage import StaticImage

class Label( StaticImage ):
    def __init__( self, parentState, text, pos, size=32, fixed=True ):
        StaticImage.__init__( self, None, None, parentState, fixed )
        self.labelText = pygame.font.Font( os.path.join( "data", "fonts", "PD-tarzeau_-_Atari_Small.ttf" ), size )
        self.text = text
        self.image = self.labelText.render( text, False, pygame.Color( 0, 0, 0 ) )
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
