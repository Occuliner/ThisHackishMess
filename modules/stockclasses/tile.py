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

"""This file defines the Tile Class."""
import pygame
#from pygame.locals import *

class Tile( pygame.sprite.Sprite ):
    """The Tile class. For use in the Floor class and editing the Floor class.\n""" \
    """Merely contains an image, size, whether the tile is solid, and if it supports kickUp."""
    def __init__( self, image, solid=False, kickUp=False ):
        pygame.sprite.Sprite.__init__( self )
        self.image = image
        self.rect = image.get_rect()
        self.rect.topleft = 0,0
        self.solid = solid
        self.kickUp = kickUp

