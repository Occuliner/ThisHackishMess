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

"""This file defines the Button class."""
from staticimage import StaticImage
import pygame

red = pygame.Color( 255, 0, 0 )

class Button( StaticImage ):
    """The Button class is a simple class for generating DevMenu buttons\n""" \
    """or for extension to create more specific Button classes."""
    button = True
    
    def __init__( self, image, pos, parentState=None, fixed=False ):
        StaticImage.__init__( self, image, pos, parentState, fixed )
        #self.parentState = parentState
    def emptyCallback( self, clickKey ):
        """Does absolutely nothing! Button.push defaults to this. push()\n""" \
        """being any given Button's effect when clicked on."""
        pass

    push = emptyCallback
