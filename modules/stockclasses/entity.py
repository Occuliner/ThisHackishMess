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
	
	def __init__( self, pos, vel, image=None, group=None, rect=None, animated=None, collidable=None, collideByPixels=None, collideId=None, collideWith=None, collideMaskMaster=None, mass=None, specialCollision=None, solid=None ):
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
		if collideByPixels is not None:
			self.collideByPixels = collideByPixels
		if collideId is not None:
			self.collideId = collideId
		if collideWith is not None:
			self.collideWith = collideWith
		if collideMaskMaster is not None:
			self.collideMaskMaster = collideMaskMaster
		if mass is not None:
			self.mass = mass
		#SpecialCollision is a function that defines a unique collision callback for objects with special collision behaviour.
		#Specials happen first, then if the objects are "solid" they have a standard anti-penetration collision too.
		if specialCollision is not None:
			self.specialCollision = specialCollision
		if solid is not None:
			self.solid = solid

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
			self.shape = pymunk.Poly( self.body, map( pymunk.vec2d.Vec2d, [ (width, 0), (width, height), (0, height), (0, 0) ] ) )
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
			self.physicsObjects = [ self.body, self.shape ]

			self.bodyId = id( self.body )
			self.shapeId = id( self.shape )
		
		#self.position = pos
		#self.pushed = [0, 0]
		#self.velocity = [0, 0]
		#self.acceleration = [0, 0]
		#self.accelerationBarrier = { '-x':False, 'x':False, '-y':False, 'y':False }
		#self.lastAcceleration = [0, 0]

		#self.maxVel = 500

		#Idle deceleration will stop an object moving at it's maxVel in 0.2 seconds.
		#self.decelRatio = 5
		#self.idleDeceleration = self.maxVel*self.decelRatio
		self.idle = [False, False]
		
		self.animated = animated
		self.animations = {'idle':{ 'fps':8, 'frames':[0] }}
		self.frames = []
		self.collideFrames = []
		self.curAnimation = self.animations['idle']

		self.createFrames()
		#if self.animated:
		#	tmpRect = self.rect.copy()
		#	tmpRect.topleft = ( 0, 0 )
		#	for y in xrange( 0, self.sheet.get_height(), self.rect.h ):
		#		for x in xrange( 0, self.sheet.get_width(), self.rect.w ):
		#			tmpRect.topleft = (x, y)
		#			self.frames.append( self.sheet.subsurface( tmpRect ) )
		#			self.collideFrames.append( self.collideMaskMaster.getGridFromRect( tmpRect ) ) 
		#else:
		#	self.frames = [ self.sheet ]
		#	self.collideFrames = [ self.collideMaskMaster ]

		self.frame = 0
		self.image = self.frames[0]
		self.collideMask = self.collideFrames[0]
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

	def addToGroup( self, *groups ):
		if self.collidable:
			for group in groups:
				if self.body not in group.playState.space.bodies:
					group.playState.space.add( self.body )
				if self.shape not in group.playState.space.shapes:
					group.playState.space.add( self.shape )
		pygame.sprite.DirtySprite.add( self, groups )

	def removeFromGroup( self, *groups ):
		if self.collidable:
			for group in groups:
				if self.body in group.playState.space.bodies:
					group.playState.space.remove( self.body )
				if self.shape in group.playState.space.shapes:
					group.playState.space.remove( self.shape )
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
						self.frames.append( self.sheet.subsurface( tmpRect ) )
						self.collideFrames.append( self.collideMaskMaster.getGridFromRect( tmpRect ) ) 
			#for y in xrange( 0, self.sheet.get_height(), self.rect.h ):
			#	for x in xrange( 0, self.sheet.get_width(), self.rect.w ):
			#		tmpRect.topleft = (x, y)
			#		self.frames.append( self.sheet.subsurface( tmpRect ) )
			#		self.collideFrames.append( self.collideMaskMaster.getGridFromRect( tmpRect ) )
		#else:
			#self.frames = [ self.sheet ]
			#self.collideFrames = [ self.collideMaskMaster ]

	def collideWithEnt( self, otherEnt ):
		clippedArea = otherEnt.rect.clip( self.rect )
		#Is there any overlap?
		if clippedArea.w != 0 and clippedArea.h != 0 and otherEnt.collideId in self.collideWith:
			#No pixel-collision?
			if ( not self.collideByPixels ) and ( not otherEnt.collideByPixels ):
				return [True, clippedArea]
			
			#Both pixel-collison?
			elif otherEnt.collideByPixels and self.collideByPixels:
				intersectGrid = self.collideMask.getGridFromRect( clippedArea ).mergeWith( otherEnt.collideMask.getGridFromRet( clippedArea ), 'and' )

			#One but not the other?
			elif otherEnt.collideByPixels:
				intersectGrid = otherEnt.collideMask.getGridFromRect( clippedArea )

			else:
			#In effect: elif self.collideByPixels:
				intersectGrid = self.collideMask.getGridFromRect( clippedArea )
			truthArea = intersectGrid.getTrueBox()

			#TruthBox of any size?
			if truthArea[2] <= 0 or truthArea[3] <= 0:
				return [False, None]
			
			truthRect = pygame.Rect( truthArea[0], truthArea[1], truthArea[2], truthArea[3] )
			return [True, truthRect]
			
			
		else:
			return [False, None]

	#
	#	pos in CollideWithBooleanGrid represents the position of the boolean grid from the origin.
	# 
	def collideWithBooleanGrid( self, booleanGrid, pos=(0,0) ):
		clippedArea = self.rect.clip( pygame.Rect( pos[0], pos[1], booleanGrid.width, booleanGrid.height ) )
		if clippedArea.w == 0 or clippedArea.h == 0:
			return [False, None]
		if self.collideByPixels:
			intersectGrid = self.collideMask.getGridFromRect( clippedArea ).mergeWith( booleanGrid.getGridFromRect( clippedArea ), 'and' )
		else:
			intersectGrid = booleanGrid.getGridFromRect( clippedArea )

		truthArea = intersectGrid.getTrueBox()

		#TruthBox of any size?
		if truthArea[2] <= 0 or truthArea[3] <= 0:
			return [False, None]
			
		truthRect = pygame.Rect( truthArea[0], truthArea[1], truthArea[2], truthArea[3] )
		return [True, truthRect]


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
		if self.collideByPixels:
			self.collideMask = self.collideFrames[ self.curAnimation['frames'][self.frame] ]

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
		
		#if abs( self.acceleration[0] ) < 0.1:
		#	self.acceleration[0] = 0.0
		#if abs( self.acceleration[1] ) < 0.1:
		#	self.acceleration[1] = 0.0

		#self.velocity[0] += self.acceleration[0]*dt
		#self.velocity[1] += self.acceleration[1]*dt

		#print dt
		
		#if self.velocity[0] != 0:# and self.acceleration[0] == 0:
		#	#print self.velocity[0],
		#	sign = self.velocity[0]/abs(self.velocity[0])
		#	self.velocity[0] -= sign*self.idleDeceleration*dt#*self.velocity[0]/self.maxVel
		#	#print self.velocity[0],
		#	if sign*self.velocity[0] < 0:
		#		self.velocity[0] = 0
		#	#print self.velocity[0]
		
		#if self.velocity[1] != 0:# and self.acceleration[1] == 0:
		#	#print self.velocity[1],
		#	sign = self.velocity[1]/abs(self.velocity[1])
		#	self.velocity[1] -= sign*self.idleDeceleration*dt#*self.velocity[1]/self.maxVel
		#	#print self.velocity[1],
		#	if sign*self.velocity[1] < 0:
		#		self.velocity[1] = 0
		#	#print self.velocity[1]
		##if self.idle[0] and self.acceleration[0] == 0:
		##if self.velocity[0] != 0:
		##	if self.velocity[0] < 0:
		##		self.velocity[0] += self.idleDeceleration*dt
		#		#if self.velocity[0] > 0:
		#		#	self.velocity[0] = 0
		##	else:
		##		self.velocity[0] -= self.idleDeceleration*dt
		#		#if self.velocity[0] < 0:
		#		#	self.velocity[0] = 0
		#		#self.velocity[0] = 0
		##if self.idle[1] and self.acceleration[1] == 0:
		##if self.velocity[1] != 0:
		##	if self.velocity[1] < 0:
		##		self.velocity[1] += self.idleDeceleration*dt
		##		if self.velocity[1] > 0:
		##			self.velocity[1] = 0
		##	else:
		##		self.velocity[1] -= self.idleDeceleration*dt
		##		if self.velocity[1] < 0:
		##			self.velocity[1] = 0
		#		#self.velocity[1] = 0
#
#		if self.maxVel < self.velocity[0]:
#			self.velocity[0] = self.maxVel
#		elif -(self.maxVel) > self.velocity[0]:
#			self.velocity[0] = -(self.maxVel)
#
#		if self.maxVel < self.velocity[1]:
#			self.velocity[1] = self.maxVel
#		elif -(self.maxVel) > self.velocity[1]:
#			self.velocity[1] = -(self.maxVel)
#
#
#		self.position[0] = ( self.velocity[0] * dt + self.position[0] )
#		self.position[1] = ( self.velocity[1] * dt * 0.5 + self.position[1] )
#
#
#		if self.position[1] + self.image.get_height() > 600:
#			self.position[1] = 600 - self.image.get_height()
#			self.velocity[1] = 0
#		elif self.position[1] < 0:
#			self.position[1] = 0
#			self.velocity[1] = 0
#			
#		if self.position[0] < 0:
#			self.position[0] = 0
#			self.velocity[0] = 0
#		elif self.position[0] + self.image.get_width() > 800:
#			self.position[0] = 800 - self.image.get_width()
#			self.velocity[0] = 0
#		
#		newx = int( round( self.position[0] ) )
#		newy = int( round( self.position[1] ) )
		if self.collidable:
			self.rect.topleft = self.body.position.x, self.body.position.y
		else:
			self.rect.topleft = int( round( self.position[0] ) ), int( round( self.position[1] ) )
		#print self.body.is_sleeping, self.body.is_static
#		self.rect.topleft = (newx, newy)
#
#		#Assume idle at end of frame
		self.idle = [True, True]
#		self.lastAcceleration = self.acceleration
#		self.acceleration = [0,0]
#		self.accelerationBarrier = { '-x':False, 'x':False, '-y':False, 'y':False }

		#Check if class has been updated.
		if self.classUpdated:
			self.frames = []
			self.collideFrames = []

			self.rect.w = self.width
			self.rect.h = self.height
			

			self.createFrames()
			#tmpRect = self.rect.copy()
			
			#tmpRect.topleft = ( 0, 0 )
			#for y in xrange( 0, self.sheet.get_height(), self.rect.h ):
			#	if y + self.height <= self.sheet.get_height():
			#		for x in xrange( 0, self.sheet.get_width(), self.rect.w ):
			#			if x + self.width <= self.sheet.get_width():
			#				tmpRect.topleft = (x, y)
			#				self.frames.append( self.sheet.subsurface( tmpRect ) )
			#				self.collideFrames.append( self.collideMaskMaster.getGridFromRect( tmpRect ) ) 
			self.classUpdated = False

		if len( self.groups() ) > 1:
			raise Exception( "An instance of Entity is in more than one group, that should probably not be happening." )

		self.pushed = [0, 0]
		
