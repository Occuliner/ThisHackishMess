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
