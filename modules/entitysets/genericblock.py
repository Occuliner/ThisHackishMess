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

from maskfromimage import *

import math

class GenericBlock( Entity ):
	width = 32
	height = 32

	playStateGroup = "genericStuffGroup"
	setName = "genericstuff"

	sheetFileName = "block.png"
	sheet = loadImage( sheetFileName )

	collideMaskMaster = booleanGridFromAlpha( sheet )
	specialCollision = None
	collideId = 2
	collideWith = set([1,2])
	collideByPixels = False
	collidable = True
	solid = True
	mass = 20
	
	def __init__( self, pos = [0,0], vel = [0,0], group=None ):
		Entity.__init__( self, pos, [0,0], None, group, pygame.Rect( 0, 0, self.width, self.height ), animated=False )
		#self.time = 0
		#self.idleDeceleration = 1000
	
	def update( self, dt ):
		#self.acceleration[0] = -2000
		#print self.idleDeceleration		
		#if self.acceleration[0] != 0.0 or self.acceleration[1] != 0.0:
		#	print self.acceleration
		Entity.update( self, dt )
		#self.time = 0
		#self.time += dt
		#print self.velocity, self.acceleration
		#self.velocity[0] = 500*math.sin( self.time*math.pi )
		#self.velocity[1] = 500*math.cos( self.time*math.pi )
		

MasterEntitySet.entsToLoad.append( GenericBlock )
