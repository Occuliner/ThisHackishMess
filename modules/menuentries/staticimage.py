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

