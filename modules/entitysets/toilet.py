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

from entity import *
import pygame
from pygame.locals import *

from masterentityset import *

class Toilet( Entity ):
	width = 16
	height = 21

	playStateGroup = "genericStuffGroup"
	setName = "genericstuff"

	sheetFileName = "toilet.png"
	colourKey = pygame.Color( 255, 0, 255 )
	sheet = loadImageNoAlpha( sheetFileName, 2 )
	sheet.set_colorkey( colourKey )

	specialCollision = None
	collidable = False
	scale = 2

	instanceSpecificVars = None

	frameRects = [ pygame.Rect( 0, 0, 32, 42 ), pygame.Rect( 32, 0, 32, 42 ), pygame.Rect( 64, 0, 22, 42 ), pygame.Rect( 86, 0, 22, 42 ) ]
	
	def __init__( self, pos = [0,0], vel = [0,0], group=None, **kwargs ):
		Entity.__init__( self, pos, [0,0], None, group, pygame.Rect( 0, 0, self.width, self.height ), animated=True, **kwargs )
		self.animations['left'] = { 'fps': 1, 'frames':[0] }
		self.animations['right'] = { 'fps': 1, 'frames':[1] }
		self.animations['forward'] = { 'fps': 1, 'frames':[3] }
		self.animations['backward'] = { 'fps': 1, 'frames':[4] }
		self.changeAnimation('left')
		if Toilet.instanceSpecificVars is None:
			attrList = list( self.__dict__.keys() )
		self.oldTag= 'left'
		self.tags['direction'] = 'left'
		if Toilet.instanceSpecificVars is None:
			Toilet.instanceSpecificVars = dict( [ ( eachKey, eachVal ) for eachKey, eachVal in self.__dict__.items() if eachKey not in attrList ] )
	
	def update( self, dt ):
		curTag = self.tags.get('direction')
		if curTag != self.oldTag and curTag in ( 'left', 'right', 'forward', 'backward' ):
			self.changeAnimation(curTag)
			self.oldTag = curTag
		Entity.update( self, dt )

MasterEntitySet.entsToLoad.append( Toilet )
