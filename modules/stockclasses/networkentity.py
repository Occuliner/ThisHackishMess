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

from imageload import loadImage, loadImageNoAlpha
from imageslice import sliceImage


def idleCentricVelocityUpdate( body, gravity, damping, dt ):
	"""
	This function is an "idle-centric" velocity updater for Pymunk.

	Basically it means that objects only have their velocity "dampen" when no net force is being exerted on them.
	"""
	if body.force.x == 0 and body.force.y == 0:
		pymunk.Body.update_velocity( body, gravity, damping, dt )
	else:
		pymunk.Body.update_velocity( body, gravity, 1.0, dt )

class NetworkEntity( pygame.sprite.DirtySprite ):
	
	#If this is true on an entity, then the Entity cannot be removed from the Entity Edit Menu.
	notDirectlyRemovable = False
	
	mass = 1
	
	#Width and Height are for the frames, bWidth and bHeight for sensor boxes, wbWidth and wbHeight for "physics" boxes.
	width, height, bWidth, bHeight, wbWidth, wbHeight = None, None, None, None, None, None
	bdx, bdy = 0, 0

	#If something is only a sensor, ie, can ghost through objects.
	pureSensor = False

	#The scale of the sprite's sheet from it's default file.
	scale = 1

	#RGB colourKey. Look it up on Pygame.
	colourKey = None

	#Whether the sprite uses per-pixel alpha
	alpha = True

	#FrameRects are all the rect areas to cut for frames, in index order, if left as none, it auto-slices.
	frameRects = None

	#Frame Positions are the x-position and y-position of the each frame relative to the physics body, (0,0) is the uppleft corner is positioned on body location, this is the default and typical state.
	framePositions = {}

	collidable = False

	specialCollision = None

	circular = False
	radius = 1
	def __init__( self, pos, vel, image=None, group=None, rect=None, animated=None ):
		pygame.sprite.DirtySprite.__init__( self )
		
		#All of these are purely so that instances CAN have their own unique one of each of these variables, but if one isn't specified, it'll use its Class's one.
		if image is not None:
			self.sheet = image
		if rect is not None:
			self.rect = rect
		if animated is not None:
			self.animated = animated
		if self.width is None:
			self.width = self.rect.w
		if self.height is None:
			self.height = self.rect.h

		
		self.rect.topleft = pos
		
		
		self.animated = animated
		self.animations = {'idle':{ 'fps':8, 'frames':[0] }}
		self.frames = []
		self.curAnimation = self.animations['idle']
		
		self.createFrames()

		self.frame = 0
		self.image = self.frames[0]
		self.maxFrameTime = 1.000/self.curAnimation['fps']
		self.frameTime = self.maxFrameTime

		self.visible = 1
		self.dirty = 2
		
		if group != None:
			self.id = len( group )
			self.addToGroup( group )
		else:
			self.id = None

		self.classUpdated = False

		self.oldPan = group.playState.panX, group.playState.panY

	def addToGroup( self, *groups ):
		if self.collidable:
			for group in groups:
				group.playState.space.add( self.physicsObjects )
		pygame.sprite.DirtySprite.add( self, groups )

	def removeFromGroup( self, *groups ):
		if self.collidable:
			for group in groups:
				group.playState.space.remove( self.physicsObjects )
		pygame.sprite.DirtySprite.remove( self, groups )

	def getPosition( self ):
		if self.collidable:
			return [self.body.position[0], self.body.position[1]]
		else:
			return [self.rect.topleft[0], self.rect.topleft[1]]

	def setPosition( self, newPos ):
		if self.collidable:
			self.body.position = list( newPos )
		else:
			self.rect.topleft = newPos[0], newPos[1]

	def createFrames( self ):
		if self.frameRects is None:
			tmpRect = self.rect.copy()
			tmpRect.topleft = ( 0, 0 )
			self.frames = sliceImage( self.sheet, tmpRect, colourKey=self.colourKey )
			if len( self.frames ) is 0:
				self.frames = [self.sheet]
		else:
			for eachFrame in self.frameRects:
				img = self.sheet.subsurface( eachFrame )
				img.set_colorkey( self.colourKey )
				self.frames.append( img )
		

	def setVisible( self, theBool ):
		if theBool:
			self.visible = 1
		else:
			self.visible = 0
		
	def nextFrame( self ):
		self.frame += 1
		if self.frame > len(self.curAnimation['frames']) - 1:
			self.frame = 0
		self.image = self.frames[ self.curAnimation['frames'][self.frame] ]
		self.frameTime = self.maxFrameTime

	def changeAnimation( self, name ):
		newAnim = self.animations[name]
		if self.curAnimation == newAnim:
			return None
		self.curAnimation = newAnim
		self.maxFrameTime = 1.000/self.curAnimation['fps']
		self.frame = -1
		self.nextFrame()
		

	def swapAnimation( self, name ):
		curFrameFraction = float(self.frame)/len( self.curAnimation['frames'] )
		newAnim = self.animations[name]
		if self.curAnimation == newAnim:
			return None
		self.curAnimation = newAnim
		self.maxFrameTime = 1.000/self.curAnimation['fps']
		self.frame = int( curFrameFraction*len( self.curAnimation['frames'] ) ) - 1
		self.nextFrame()
		
	def getMomentumOnAxis( self, axis ):
		return self.mass*self.velocity[axis]

	def changeMaxVel( self, newMax):
		self.maxVel = newMax
	
	def getVelocitySize( self ):
		return ( self.velocity[0]**2 + self.velocity[1]**2 )**0.5
	
	def getNetAccel( self ):
		signX = cmp( self.acceleration[0], 0 )
		signY = cmp( self.acceleration[1], 0 )
		return ( self.acceleration[0] - signX*self.idleDeceleration, self.acceleration[1] - signY*self.idleDeceleration )
	
	def readyAccel( self, dt ):
		"""
		This method is a dummy method to be replaced by child classes.
		Basically you call this for things that ONLY effect acceleration, before everything else in the frame starts."""
		pass

	def kill( self ):
		if self.collidable:
			self.groups()[0].playState.space.remove( self.physicsObjects )
		pygame.sprite.DirtySprite.kill( self )
		

	def update( self, dt ):
		if self.animated:
			self.frameTime -= dt
			if self.frameTime <= 0:
				self.nextFrame()
				#self.frameTime = self.maxFrameTime
		
		self.rect.x -= self.oldPan[0]
		self.rect.y -= self.oldPan[1]

		if self.collidable:
			framePosition = self.framePositions.get( self.curAnimation['frames'][self.frame], (0,0) )
			self.rect.topleft = self.body.position.x+framePosition[0], self.body.position.y+framePosition[1]
			#Behold, a cheap hack to fix circular objects physics and visuals not lining up.
			if self.circular:
				self.rect.y -= self.height/2
				self.rect.x -= self.width/2

		listOfGroups = self.groups()
		if len( listOfGroups ) > 0:
			npx = listOfGroups[0].playState.panX
			npy = listOfGroups[0].playState.panY
		else:
			npx, npy = 0, 0
		self.rect.x += npx
		self.rect.y += npy

		self.oldPan = npx, npy


		#Check if class has been updated.
		if self.classUpdated:
			self.frames = []

			self.rect.w = self.width
			self.rect.h = self.height
			

			self.createFrames()
			self.classUpdated = False

		if len( self.groups() ) > 1:
			raise Exception( "An instance of Entity is in more than one group, that should probably not be happening." )
