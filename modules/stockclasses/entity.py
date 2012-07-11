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

import pygame, pymunk

#sys.path.append( "../../" )

#from maskcompare import *
from imageload import loadImage, loadImageNoAlpha

class EntityGroup( pygame.sprite.LayeredDirty ):
	def __init__( self, name="Unnamed" ):
		pygame.sprite.LayeredDirty.__init__( self )
		self.name = name
		self.playState = None
	def add( self, *sprites, **kwargs ):
		for sprite in sprites:
			#if hasattr( sprite, "shape" ):
			if sprite.collidable:
				if hasattr( sprite, "sensorBox" ):
					if sprite.sensorBox not in self.playState.space.shapes:
						self.playState.space.add( sprite.sensorBox )
				if sprite.shape not in self.playState.space.shapes:
					self.playState.space.add( sprite.shape )
				if sprite.body not in self.playState.space.bodies:
					self.playState.space.add( sprite.body )
		pygame.sprite.LayeredDirty.add( self, sprites, kwargs )

	def update( self, dt ):
		for each in iter( self ):
			each.update( dt )
			
	def readyAccel( self, dt ):
		for each in iter( self ):
			each.readyAccel( dt )

def idleCentricVelocityUpdate( body, gravity, damping, dt ):
	"""
	This function is an "idle-centric" velocity updater for Pymunk.

	Basically it means that objects only have their velocity "dampen" when no net force is being exerted on them.
	"""
	if body.force.x == 0 and body.force.y == 0:
		pymunk.Body.update_velocity( body, gravity, damping, dt )
	else:
		pymunk.Body.update_velocity( body, gravity, 1.0, dt )

class Entity( pygame.sprite.DirtySprite ):

	notDirectlyRemovable = False
	mass = 1
	#Width and Height are for the frames, bWidth and bHeight for sensor boxes, wbWidth and wbHeight for "physics" boxes.
	width, height, bWidth, bHeight, wbWidth, wbHeight = None, None, None, None, None, None
	bdx, bdy = 0, 0
	pureSensor = False
	scale = 1
	colourKey = None
	alpha = True
	def __init__( self, pos, vel, image=None, group=None, rect=None, animated=None, collidable=None, collideId=None, collideWith=None, mass=None, specialCollision=None, solid=None, pureSensor=None ):
		pygame.sprite.DirtySprite.__init__( self )
		
		#All of these are purely so that instances CAN have their own unique one of each of these variables, but if one isn't specified, it'll use its Class's one.
		if image is not None:
			self.sheet = image
		if rect is not None:
			self.rect = rect
		if animated is not None:
			self.animated = animated
		if collidable is not None:
			self.collidable = collidable
		if collideId is not None:
			self.collideId = collideId
		if collideWith is not None:
			self.collideWith = collideWith
		if mass is not None:
			self.mass = mass
		#SpecialCollision is a function that defines a unique collision callback for objects with special collision behaviour.
		#Specials happen first, then if the objects are "solid" they have a standard anti-penetration collision too.
		if specialCollision is not None:
			self.specialCollision = specialCollision
		if solid is not None:
			self.solid = solid
		if pureSensor is not None:
			self.pureSensor = pureSensor
		if self.width is None:
			self.width = self.rect.w
		if self.height is None:
			self.height = self.rect.h

		if self.collidable:
			self.body = pymunk.Body( self.mass, 1e100 )
			#self.body.position = pymunk.vec2d.Vec2d( pos )
			self.body.velocity_limit = 200
			self.body.angular_velocity_limit = 0
			self.velocity_func = idleCentricVelocityUpdate
			self.body.velocity_func = idleCentricVelocityUpdate

			#self.shape = pymunk.Poly( self.body, [ self.rect.bottomright, self.rect.topright, self.rect.topleft, self.rect.bottomleft ] )
			#self.shape = pymunk.Circle( self.body, 5 )
			width, height = self.rect.width, self.rect.height
			self.physicsObjects = [self.body]

			if self.bHeight is not None and self.bWidth is not None:
				self.sensorBox = pymunk.Poly( self.body, map( pymunk.vec2d.Vec2d, [ (self.bWidth+self.bdx, 0+self.bdy), (self.bWidth+self.bdx, self.bHeight+self.bdy), (0+self.bdx, self.bHeight+self.bdy), (0+self.bdx, 0+self.bdy) ] ) )
				self.sensorBox.sensor = True
				self.sensorBox.collision_type = 2
				self.sensorBox.entity = self
				self.sensorId = id( self.sensorBox )
				self.physicsObjects.append( self.sensorBox )
			if self.wbHeight is not None and self.wbWidth is not None:
				self.shape = pymunk.Poly( self.body, map( pymunk.vec2d.Vec2d, [ (self.wbWidth+self.wbdx, 0+self.wbdy), (self.wbWidth+self.wbdx, self.wbHeight+self.wbdy), (0+self.wbdx, self.wbHeight+self.wbdy), (0+self.wbdx, 0+self.wbdy) ] ) )
			elif height is not None and width is not None:
				self.shape = pymunk.Poly( self.body, map( pymunk.vec2d.Vec2d, [ (width, 0), (width, height), (0, height), (0, 0) ] ) )
			else:
				self.shape = pymunk.Poly( self.body, map( pymunk.vec2d.Vec2d, [ (self.rect.w, 0), (self.rect.w, self.rect.h), (0, self.rect.h), (0, 0) ] ) )
			self.physicsObjects.append( self.shape )
			self.shape.sensor = not self.solid
			self.shape.elasticity = 0.0
			self.shape.friction = 0.5
			self.collision_type = 0
			self.body.position = pymunk.vec2d.Vec2d( pos )
			if self.solid:
				self.shape.collision_type = 1
			else:
				self.shape.collision_type = 2
			self.shape.entity = self
			#group.playState.space.add( self.body, self.shape )
			#self.physicsObjects = [ self.body, self.shape ]

			self.bodyId = id( self.body )
			self.shapeId = id( self.shape )
		else:
			self.rect.topleft = pos
		
		self.idle = [False, False]
		
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

		self.tags = {}
		self.children = []
		self.classUpdated = False

		self.oldPan = group.playState.panX, group.playState.panY

	def addToGroup( self, *groups ):
		if self.collidable:
			for group in groups:
				group.playState.space.add( self.physicsObjects )
				#if hasattr( self, "sensorBox" ):
				#	if self.sensorBox not in group.playState.space.shapes:
				#		group.playState.space.add( self.sensorBox )
				#if self.body not in group.playState.space.bodies:
				#	group.playState.space.add( self.body )
				#if self.shape not in group.playState.space.shapes:
				#	group.playState.space.add( self.shape )
		pygame.sprite.DirtySprite.add( self, groups )

	def removeFromGroup( self, *groups ):
		if self.collidable:
			for group in groups:
				group.playState.space.remove( self.physicsObjects )
				#if hasattr( self, "sensorBox" ):
				#	if self.sensorBox in group.playState.space.shapes:
				#		group.playState.space.remove( self.sensorBox )
				#if self.body in group.playState.space.bodies:
				#	group.playState.space.remove( self.body )
				#if self.shape in group.playState.space.shapes:
				#	group.playState.space.remove( self.shape )
		pygame.sprite.DirtySprite.remove( self, groups )

	def getPosition( self ):
		if self.collidable:
			return list( self.body.position[0], self.body.position[1] )
		else:
			return list( self.position )

	def setPosition( self, newPos ):
		if self.collidable:
			self.body.position = list( newPos )
		else:
			self.position = list( newPos )

	def createFrames( self ):
		#if self.animated:
		tmpRect = self.rect.copy()
		tmpRect.topleft = ( 0, 0 )
		for y in xrange( 0, self.sheet.get_height(), self.rect.h ):
			if y + self.height <= self.sheet.get_height():
				for x in xrange( 0, self.sheet.get_width(), self.rect.w ):
					if x + self.width <= self.sheet.get_width():
						tmpRect.topleft = (x, y)
						tmpSurface = self.sheet.subsurface( tmpRect )
						tmpSurface.set_colorkey( self.colourKey )
						self.frames.append( tmpSurface )
		if len( self.frames ) is 0:
			self.frames = [self.sheet]

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

	def changeAnimation( self, name ):
		newAnim = self.animations[name]
		if self.curAnimation == newAnim:
			return None
		self.curAnimation = newAnim
		self.maxFrameTime = 1.000/self.curAnimation['fps']
		self.frame = -1
		self.nextFrame()

	#This function changes to a new animation, but keeps the same PERCENTAGE completion of animation, (eg, if one animation playing and is half way through, a swapped in animation will start at halfway )
	def swapAnimation( self, name ):
		curFrameFraction = float(self.frame)/len( self.curAnimation['frames'] )
		#print curFrameFraction
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
		#self.idleDeceleration = self.decelRatio*self.maxVel
	
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
		#I'm adding a new premise to the physics system, acceleration is reset at the end of each tick.
		if self.animated:
			self.frameTime -= dt
			if self.frameTime <= 0:
				self.nextFrame()
				self.frameTime = self.maxFrameTime
		
		self.rect.x -= self.oldPan[0]
		self.rect.y -= self.oldPan[1]

		if self.collidable:
			self.rect.topleft = self.body.position.x, self.body.position.y

		npx = self.groups()[0].playState.panX
		npy = self.groups()[0].playState.panY

		self.rect.x += npx
		self.rect.y += npy

		self.oldPan = npx, npy

		#else:
		#	self.rect.topleft = int( round( self.position[0] ) ), int( round( self.position[1] ) )
#		#Assume idle at end of frame
		self.idle = [True, True]

		#Check if class has been updated.
		if self.classUpdated:
			self.frames = []

			self.rect.w = self.width
			self.rect.h = self.height
			

			self.createFrames()
			self.classUpdated = False

		if len( self.groups() ) > 1:
			raise Exception( "An instance of Entity is in more than one group, that should probably not be happening." )

		self.pushed = [0, 0]
