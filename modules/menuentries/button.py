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
