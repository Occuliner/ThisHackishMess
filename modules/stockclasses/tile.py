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

