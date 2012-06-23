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
import pygame, os
from pygame.locals import *

from masterentityset import *

from maskfromimage import *

from picklestuff import *

def levelWarpFunc( givenWarp, givenObject ):
	curPlayState = givenObject.groups()[0].playState
	if givenObject in curPlayState.playersGroup:
		givenWarp.collidedWith.add( givenObject )
		if givenObject not in givenWarp.ignore:
			givenObject.removeFromGroup( curPlayState.playersGroup )
			for each in givenObject.children:
				each.removeFromGroup( curPlayState.playersGroup )
			curPlayState.swap( loadPlayState( os.path.join( "data", "maps", givenWarp.tags["warpDest"] ), curPlayState.floor.tileSet ) )
			for each in curPlayState.levelWarpGroup:
				if each.tags.get("warpKey") == givenWarp.tags["warpKey"]:
					targetWarp = each
					break
			givenObject.body.position = targetWarp.body.position.x, targetWarp.body.position.y
			givenObject.addToGroup( curPlayState.playersGroup )
			for each in givenObject.children:
				each.addToGroup( curPlayState.playersGroup )
			targetWarp.ignore.add( givenObject )
			targetWarp.collidedWith.add( givenObject )
			curPlayState.rerenderEverything = True

def queueLoad( givenWarp, givenObject ):
	curPlayState = givenObject.groups()[0].playState
	curPlayState.postStepQueue.append( ( levelWarpFunc, givenWarp, givenObject ) )

class LevelWarp( Entity ):
	width = 16
	height = 16

	playStateGroup = "levelWarpGroup"
	setName = "levelwarp"

	sheetFileName = "block.png"
	sheet = loadImage( sheetFileName )

	collideMaskMaster = booleanGridFromAlpha( sheet )
	specialCollision = queueLoad
	collideId = 2
	collideWith = set([1])
	collideByPixels = False
	collidable = True
	solid = False
	mass = 20
	
	def __init__( self, pos = [0,0], vel = [0,0], group=None ):
		Entity.__init__( self, pos, [0,0], None, group, pygame.Rect( 0, 0, self.width, self.height ), animated=False )
		#self.shape.collision_type = 1
		self.tags["warpKey"] = "prime"
		self.tags["warpDest"] = "testthingy"
		self.ignore = set([])
		self.collidedWith = set([])
	
	def update( self, dt ):
		Entity.update( self, dt )
		for each in self.groups()[0].playState.playersGroup:
			if each not in self.collidedWith and each in self.ignore:
				self.ignore.remove( each )
		self.collidedWith = set([])
		

MasterEntitySet.entsToLoad.append( LevelWarp )
