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

"""This file defines the StaticImage class, for use in the DevMenu.\n""" \
"""This is mainly just extended on later for Button's, but it can \n""" \
"""be used for any random visual element in the DevMenu."""
import pygame
#from pygame.locals import *

class StaticImage( pygame.sprite.Sprite ):
    """The StaticImage class, used for any random visual element in the DevMenu.\n""" \
    """Mainly just extended on by Button, which is in turn extended on by other class types."""
    button = False
    def __init__( self, image, pos, parentState=None, fixed=False ):
        pygame.sprite.Sprite.__init__( self )
        if image is not None:
            self.image = image
        if pos is not None:    
            self.rect = self.image.get_rect()
            self.rect.topleft = pos
        if parentState is not None:
            self.parentState = parentState
        self.classUpdated = False
        self.fixed = fixed

