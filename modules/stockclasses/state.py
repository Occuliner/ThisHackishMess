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

import pygame, pymunk, sys, gc
#from pygame.locals import *
from booleangrid import BooleanGrid
from collisionstate import CollisionState
from linevisualiser import LineVisualiser
from soundmanager import SoundManager

"""This module defines the PlayState class."""

def callSpeshulEffect( space, arbiter, *args, **kwargs ):
	objA, objB = arbiter.shapes[0].entity, arbiter.shapes[1].entity
	if hasattr( objA, "specialCollision" ):
		if objA.specialCollision is not None:
			objA.specialCollision( objB )
	if hasattr( objB, "specialCollision" ):
		if objB.specialCollision is not None:
			objB.specialCollision( objA )
	return True

class PlayState:
	""" The PlayState class.
	Maintains a list of all entity groups, can update them all, draw them all,
	return a list of all their sprites, and run the collision system."""
	def __init__( self ):
		self.groups = []
		self.floor = None
		self.space = pymunk.Space()
		self.space.gravity = ( 0.0, 0.0 )
		self.space.damping = 0.00025
		#self.space.set_default_collision_handler()
		self.space.add_collision_handler( 1, 2, callSpeshulEffect )
		self.space.add_collision_handler( 2, 2, callSpeshulEffect )
		self.speshulCaller = callSpeshulEffect
		self.postStepQueue = []


		self.spaceGhost = None
		
		self.forceUpdateEverything = False

		self.boundaryBody = pymunk.Body()
		self.boundaries = []
		
		#A list of int values that represent the index values of a 
		#group in self.groups, each group is drawn in order of the
		# values in this list. Use addGroup() to add one, by default 
		# it puts the group in the last index of self.drawOrder,
		# unless passed a index value.
		self.drawOrder = []

		self.curInputDict = {}
		
		self.playersGroup = None

		self.namedGroups = { 'playersGroup':self.playersGroup }

		self.lineVisualiser = LineVisualiser( self )

		self.rerenderEverything = False

		self.soundManager = SoundManager()

		self.fileName = "Untitled"

	def addBoundary( self, point1, point2 ):
		newSeg = pymunk.Segment( self.boundaryBody, point1, point2, 1 )
		self.boundaries.append( newSeg )
		self.space.add_static( newSeg )

	def removeBoundary( self, givenSeg ):
		self.boundaries.remove( givenSeg )
		self.space.remove_static( givenSeg )

	def swap( self, newState ):
		self.__dict__ = newState.__dict__
		for eachGroup in self.groups:
			eachGroup.playState = self
		gc.collect()
		#Pymunk is leaky for me.
		for obj in gc.garbage:
			if obj.__class__.__name__ is "Space":
				del obj.__dict__['_handlers']
		del gc.garbage[:]
		
	def addGroup(self, group, indexValue=None, isPlayerGroupBool=False, name=None):
		"""addGroup(self, group, indexValue=None, isPlayerGroupBool=False, name=None)

		Add's an entity group to the PlayState.

		If indexValue specifies the draw-order, defaults to last.
		isPlayerGroupBool specifies if the group is a group of players
		(ie, a group that will be sent input dictionaries).
		If a "name" is given, set PlayState.name = group."""
		
		group.playState = self
		self.groups.append( group )
		newIndex = len( self.groups ) - 1
		if indexValue == None:
			self.drawOrder.append( newIndex )

		else:
			self.drawOrder.insert( indexValue, newIndex )
		
		if isPlayerGroupBool:
			self.playersGroup = group
		
		if name is not None:
			self.namedGroups[name] = group
			setattr( self, name, group )

	def update( self, dt ):
		"""A generic update function.
		Sends input dictionaries to playerGroups.
		Updates all the child groups, runs the collision system."""
		if self.playersGroup is not None and len( self.curInputDict ) > 0:
			for eachPlayer in self.playersGroup.sprites():
				eachPlayer.sendInput( self.curInputDict )
			self.curInputDict = {}
		
		#for eachGroup in self.groups:
		#	eachGroup.readyAccel( dt )
		
		self.space.step( 1.0/60.0 )
		for eachTriplet in self.postStepQueue:
			eachTriplet[0]( eachTriplet[1], eachTriplet[2] )
		self.postStepQueue = []
		#self.collideSystem( dt )
		
		for eachGroup in self.groups:
			eachGroup.update( dt )
		#self.collideSystem( dt )
		#print 1.0000/dt, len( self.sprites() )
			
		

	def sendInput( self, inputDict ):
		"""Simply sets PlayState.curInputDict to a given input dictionary, 
		for use in PlayState.update()"""
		self.curInputDict = inputDict

	def collideSystem( self, dt ):
		"""
		collideSystem( self )

		Returns NoneType
		
		This function is the function called by the PlayState to run collision on every sprite with every other sprite in the PlayState.
		
		First the function takes all the sprites in the PlayState and makes a list with all that are set to be collidable.

		Then the function iterates over each sprite. First creating the list of sprites it can collide with ( is in its collideWith list ) that haven't been checked yet.
		Then colliding the current sprite with everyother sprite, and getting the result.  The system can then do something as a response based off what the two sprites are.

		If objects collide, the system adds then to a solidCollisionPair list, which is then iterating over by descending-stability order.

		The function then removes the checked sprite from the list of those not checked yet, to improve performance.
		"""

		collidableSprites = [each for each in self.sprites() if each.collidable]
		#print len(collidableSprites)
		spritesNotCheckedYet = list( collidableSprites )
		removeFromTheList = spritesNotCheckedYet.remove
		
		theNewCollisionState = CollisionState()
		for eachSprite in collidableSprites:

			removeFromTheList( eachSprite )
			checkThese = (each for each in spritesNotCheckedYet if each.collideId in eachSprite.collideWith)
			
			esCollideWithEntLocal = eachSprite.collideWithEnt
			esSpecialCollision = eachSprite.specialCollision is not None
			
			#Non loop-unrolled version.
			#for otherSprite in checkThese:
			#	resultOfSpriteCollide = esCollideWithEntLocal( otherSprite )
			#	if resultOfSpriteCollide[0]:
			#		#if eachSprite.specialCollision is not None:
			#		if esSpecialCollision:
			#			eachSprite.specialCollision( eachSprite, otherSprite )
			#		if otherSprite.specialCollision is not None:
			#			otherSprite.specialCollision( otherSprite, eachSprite )
			#		if eachSprite.solid and otherSprite.solid:
			#			momentumCollideRects( eachSprite, otherSprite, resultOfSpriteCollide[1] )	
			
			if eachSprite.solid and esSpecialCollision:
				for otherSprite in checkThese:
					resultOfSpriteCollide = esCollideWithEntLocal( otherSprite )
					if resultOfSpriteCollide[0]:
						#if eachSprite.specialCollision is not None:
						eachSprite.specialCollision( otherSprite, dt )
						if otherSprite.specialCollision is not None:
							otherSprite.specialCollision( eachSprite, dt )
						if otherSprite.solid:
							#momentumCollideRects( eachSprite, otherSprite, resultOfSpriteCollide[1], dt )
							theNewCollisionState.addCollision( eachSprite, otherSprite, resultOfSpriteCollide[1] )
			elif eachSprite.solid:
				for otherSprite in checkThese:
					resultOfSpriteCollide = esCollideWithEntLocal( otherSprite )
					if resultOfSpriteCollide[0]:
						if otherSprite.specialCollision is not None:
							otherSprite.specialCollision( eachSprite, dt )
						if otherSprite.solid:
							#momentumCollideRects( eachSprite, otherSprite, resultOfSpriteCollide[1], dt )
							theNewCollisionState.addCollision( eachSprite, otherSprite, resultOfSpriteCollide[1] )
			elif esSpecialCollision:
				for otherSprite in checkThese:
					resultOfSpriteCollide = esCollideWithEntLocal( otherSprite )
					if resultOfSpriteCollide[0]:
						if eachSprite.specialCollision is not None:
							eachSprite.specialCollision( otherSprite, dt )
						#if otherSprite.specialCollision is not None:
						#	otherSprite.specialCollision( eachSprite, dt )
		#print theNewCollisionState.collisionXObjects, theNewCollisionState.collisionYObjects
		theNewCollisionState.applyCollisions()
		for eachSprite in ( each for each in collidableSprites if each.solid ):
			resultOfSolid = eachSprite.collideWithBooleanGrid(self.floor.solidMap, pos=(0,0))
			if resultOfSolid[0]:
				#inelasticCollideOneRect( eachSprite, resultOfSolidMapCollide[1] )
				pass
			
			

		

		#print "STUB! make PlayState.collideSystem() collide eachEnt with the PlayState's solidMap"

	def sprites( self ):
		"""Returns a list of all the sprites in all the entity groups in the PlayState."""
		#sumList = set([])
		sumList = []
		for eachSpriteList in [ someGroup.sprites() for someGroup in self.groups ]:
			#sumList = sumList.union( eachSpriteList )
			sumList.extend( eachSpriteList )
		return sumList

	def draw( self, surface ):
		"""Draw all the child entity groups in PlayState, returning changed area rects"""
		changeRects = []
		self.floor.draw( surface )
		#for eachVal in self.drawOrder:
		#	changeRects.extend( self.groups[eachVal].draw( surface ) )
		
		renderList = sorted( self.sprites(), lambda x, y: cmp( x.rect.bottom, y.rect.bottom ) )
		#I probably shouldn't be doing this.
		tmpDrawGroup = pygame.sprite.LayeredDirty( renderList )
		changeRects.extend( tmpDrawGroup.draw( surface ) )
		tmpDrawGroup.empty()
		del tmpDrawGroup
		
		changeRects.extend( self.lineVisualiser.draw( surface ) )
		
		if self.rerenderEverything:
			changeRects.extend( [ pygame.Rect( 0, 0, 800, 600 ) ] )
			self.rerenderEverything = False
		return changeRects

	#
	#
	#	This function, __getitem__, takes a value, if that value is a string, it looks for a group in PlayState.groups that has that string as entityGroup.name.
	#	If that value is an int, it returns the group at that index value in self.groups.
	#
	
	def __getitem__( self, value ):
		if type( value ) == str:
			for eachGroup in self.groups:
				if eachGroup.name == value:
					return eachGroup
			raise Exception("No group in PlayState by name: " + value)
		elif type( value ) == int:
			return self.groups[value]

		else:
			raise Exception("PlayState.__getitem__ only takes strs or ints, got: " + str(type( value )) )
