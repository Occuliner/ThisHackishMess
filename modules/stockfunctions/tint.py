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
from pygame.locals import *

def tint( surface, colour, original=None ):
    tintSurf = pygame.Surface( surface.get_size() ).convert_alpha()
    tintSurf.fill( colour )
    if original != None:
        surface.blit( original, (0,0) )
    surface.blit( tintSurf, (0,0), special_flags=BLEND_RGB_MULT )
