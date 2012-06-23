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

import pygame, os

from pygame.locals import *

from scale import *

def loadImage( fileName ):
	image = scaleSurface( pygame.image.load( os.path.join( "data", "graphics", fileName ) ).convert_alpha(), 2 )
        #image = pygame.transform.scale( image, ( image.get_width()*2, image.get_height()*2 ) )
	return image

def loadImageNoAlpha( fileName ):
	image = scaleSurface( pygame.image.load( os.path.join( "data", "graphics", fileName ) ).convert(), 2 )
        #image = pygame.transform.scale( image, ( image.get_width()*2, image.get_height()*2 ) )
	return image
