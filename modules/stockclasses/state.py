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

import pygame, pymunk, sys, gc, logging
import extern_modules.pygnetic as pygnetic
#from pygame.locals import *
from linevisualiser import LineVisualiser
from soundmanager import SoundManager
from idsource import IdSource
from networkserver import NetworkServer
from networkclient import NetworkClient
from modules.networkents.mindlessentholder import *

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
		
		#If this is true, devtools will class update EVERYTHING.
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

		self.hudList = []
		
		self.fileName = "Untitled"

		self.hardBlockInput = False

		#These to variables are the displacement from the state's (0,0) and the screen's (0,0), so they can be used for panning.
		self.panX, self.panY = 0, 0

		#This is the idSource, I use it for give ids to Entitys.
		self.idSource = IdSource()

	
		self.isClient = False
		self.isHost = False
		self.networkRate = 20.0
		self.networkTicker = 0
		self.networkNode = None
		self.networkEntHolder = None
		self.networkingStarted = False

	def initNetworking( self ):
		if not self.networkingStarted:
			pygnetic.init(logging_lvl=logging.DEBUG)
			self.networkingStarted = True

	def hostGame( self ):
		self.isHost = True
		self.initNetworking()
		self.networkNode = NetworkServer( playState=self )

	def connectToGame( self ):
		self.isClient = True
		self.networkEntHolder = MindlessEntHolder()
		self.initNetworking()
		self.networkNode = NetworkClient( self, self.networkEntHolder.dictOfEnts )
		self.networkNode.connect( "localhost", 1337 )

	def addBoundary( self, point1, point2 ):
		newSeg = pymunk.Segment( self.boundaryBody, point1, point2, 1 )
		self.boundaries.append( newSeg )
		self.space.add( newSeg )

	def removeBoundary( self, givenSeg ):
		self.boundaries.remove( givenSeg )
		self.space.remove( givenSeg )

	def swap( self, newState ):
		self.__dict__ = newState.__dict__
		for eachGroup in self.groups:
			eachGroup.playState = self
		for eachKey, eachVal in self.namedGroups.items():
			setattr( self, eachKey, eachVal )
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
			self.namedGroups['playersGroup'] = group
			self.playersGroup = group
		
		if name is not None:
			self.namedGroups[name] = group
			setattr( self, name, group )

	def update( self, dt ):
		"""A generic update function.
		Sends input dictionaries to playerGroups.
		Updates all the child groups, runs the collision system."""
		
		if not self.hardBlockInput:
			if self.playersGroup is not None and len( self.curInputDict ) > 0:
				for eachPlayer in self.playersGroup.sprites():
					eachPlayer.sendInput( self.curInputDict )
			
			for eachElement in self.hudList:
				eachElement.sendInput( self.curInputDict )
		self.curInputDict = {}
		
		
		self.space.step( 1.0/60.0 )
		for eachTriplet in self.postStepQueue:
			eachTriplet[0]( eachTriplet[1], eachTriplet[2] )
		self.postStepQueue = []
		
		for eachGroup in self.groups:
			eachGroup.update( dt )

		for eachElement in self.hudList:
			eachElement.update( dt )

		self.soundManager.update( dt )

		if self.isHost or self.isClient:
			if self.networkTicker >= int(60.0/self.networkRate):
				self.networkNode.update()
				self.networkTicker = -1
			self.networkTicker += 1

	def sendInput( self, inputDict ):
		"""Simply sets PlayState.curInputDict to a given input dictionary, 
		for use in PlayState.update()"""
		self.curInputDict = inputDict

	def sprites( self ):
		"""Returns a list of all the sprites in all the entity groups in the PlayState."""
		sumList = []
		for eachSpriteList in [ someGroup.sprites() for someGroup in self.groups ]:
			sumList.extend( eachSpriteList )
		return sumList

	def draw( self, surface ):
		"""Draw all the child entity groups in PlayState, returning changed area rects"""
		changeRects = []
		self.floor.draw( surface, ( self.panX, self.panY ) )
		#for eachVal in self.drawOrder:
		#	changeRects.extend( self.groups[eachVal].draw( surface ) )
		
		renderList = sorted( self.sprites(), lambda x, y: cmp( x.rect.bottom, y.rect.bottom ) )
		#I probably shouldn't be doing this.
		tmpDrawGroup = pygame.sprite.LayeredDirty( renderList )
		changeRects.extend( tmpDrawGroup.draw( surface ) )
		tmpDrawGroup.empty()
		del tmpDrawGroup
		
		changeRects.extend( self.lineVisualiser.draw( surface, (self.panX, self.panY) ) )

		for eachElement in self.hudList:
			eachElement.draw( surface )

		changeRects.extend( [ each.rect for each in self.hudList ] )
		
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
