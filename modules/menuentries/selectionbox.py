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

import pygame

from staticimage import StaticImage

class SelectionBox( StaticImage ):
    red = pygame.Color( 255, 0, 0, 255 )
    empty = pygame.Color( 0, 0, 0, 0 )
    def __init__( self, rect, parentState ):
        StaticImage.__init__( self, None, None, parentState )
        self.image = pygame.Surface( ( rect.w, rect.h ) ).convert_alpha()
        self.image.fill( self.empty )
        self.rect = rect.copy().move( -parentState.x, -parentState.y )
        pygame.draw.rect( self.image, self.red, self.rect.move( -(self.rect.left), -(self.rect.top) ), 2 )
