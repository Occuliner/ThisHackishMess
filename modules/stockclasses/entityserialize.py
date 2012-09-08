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

"""This module contains the pre-processer class for creating simple representations of Entity objects for use with serialization."""
import pygame

from physicsserialize import *

class EntityGhost:
	"""This is a Ghost for Entity types.
	Really, it only specifies things that aren't automatically created by the class' __init__.
	That's just entity location, animation details (Current animation, frame time counters etc), references to the Entitie's physics-objects, the Entities's children entities, its tags, oldPan data, and any instance specific data the system can identify."""
	def __init__( self, theEntity ):


		#Grab the class name of the Entity.
		self.className = theEntity.__class__.__name__


		## ANIMATION STUFF

		#Grab the current anim.
		self.curAnimationName = None
		for eachKey, eachVal in theEntity.animations.items():
			if eachVal == theEntity.curAnimation:
				self.curAnimationName = eachKey
				break
		if self.curAnimationName is None:
			raise Exception( "Couldn't find the animation on the given Entity in the EntityGhost __init__. This really should not be happening." )
		
		#Grab the current frame
		self.frame = theEntity.frame
		#Grab the current frameTime
		self.frameTime = theEntity.frameTime
		

		## PAN STUFF Grab the oldPan.
		self.oldPan = theEntity.oldPan


		## TAGS STUFF Grab the tags.
		self.tags = theEntity.tags


		#Get the Entity location
		if theEntity.collidable:
			self.loc = vecToTuple( theEntity.body.position )
		else:
			self.loc = theEntity.rect.topleft


		## PHYSICS STUFF

		#Only on collidables
		if theEntity.collidable:
			#Get a Ghost of the body.
			self.bodyGhost = BodyGhost( theEntity.body )
			#Get a Ghost of the standard shape, don't bother using PolyGhost as we don't need point-data.
			self.shapeGhost = ShapeGhost( theEntity.shape )
			#Get a Ghost of the sensor box, or None if not applicable.
			if hasattr( theEntity, "sensorBox" ):
				self.sensorGhost = ShapeGhost( theEntity.sensorBox )
			else:
				self.sensorGhost = None

		## CHILDREN STUFF

		#Get the childrens' ids.
		self.childrenIds = [ id( each ) for each in theEntity.children ]


		## INSTANCE SPECIFIC 

		#Create an empty dict to hold them all.
		self.instanceSpecificVars = {}
		#Iterate over the vars.
		for eachKey, eachVal in theEntity.instanceSpecificVars:
			#Get the type string.
			typeString = str( type(eachVal) )


			#PUT TESTS FOR SUPPORTED SERIALIZABLE PYGAME FORMATS. Such as Surfaces.


			#Make sure it's not in the pygame or pygnetic modules
			if 'pygame' in typeString or 'pygnetic' in typeString:
				#Raise an exception in this scenario.
				raise Exception( "You appear to be trying to seralize an Entity of type " + str( type( theEntity ) ) + 
					"with a pygame-class or pygnetic-class instanceSpecificVarible, " + eachKey + ", of type " + typeString +
					" .The serializer will never do this for you to avoid license issues with the LGPL Pygame and Pygnetic." +
					" You should consider adding serialization support for this class type to the entity serialize module." )
			else:
				#Otherwise, assume it's safe to add
				self.instanceSpecificVars[eachKey] = eachVal

	def resurrect( self, classDefs, playState ):
		"""This is the standard resurrect function. It takes a dict of ClassName:Class for finding the right constructor to call,
		 and the playState as parameters."""


		#Get the appropriate class def.
		classDef = classDefs[self.className]
		
		#Get the dest group.
		destGroup = getattr( playState, classDef.playStateGroup )


		#Init the instance.
		theInst = classDef( self.loc, group=destGroup )


		#Set all the Ghost data onto the new physics objects if applicable.
		if theInst.collidable:
			#First the body
			self.bodyGhost.resurrectOntoGiven( theInst.body )
			#Then the shape.
			self.shapeGhost.resurrectOntoGiven( theInst.shape )
			#Then the sensorBox, if applicable.
		 	if self.sensorGhost is not None:
				self.sensorGhost.resurrectOntoGiven( theInst.sensorBox )


		#Now set the tags.
		theInst.tags = self.tags


		#Pans
		theInst.oldPan = self.oldPan


		#Set the animation
		theInst.curAnimation = theInst.animations[self.curAnimationName]
		#Set one before the current frame.
		theInst = self.frame - 1
		#Use nextFrame to get to the current frame, and a clean way to make sure the image updates.
		theInst.nextFrame()
		#Now set the correct frameTime.
		theInst.frameTime = self.frameTime


		#Now set the instance specific vars.
		for eachKey, eachVal in self.instanceSpecificVars:
			setattr( theInst, eachKey, eachVal )

		return theInst

	def resurrectNetworked( self, classDefs, playState ):
		"""This is the networked resurrect function. It creates network-entities.
		It takes a dict of ClassName:Class for finding the right constructor to call,
		 and the playState as parameters."""


		#Get the appropriate class def.
		classDef = classDefs[self.className+"Network"]
		
		#Get the dest group.
		destGroup = getattr( playState, classDef.playStateGroup )


		#TO DO! Make it so that an object must either be set to neverCollides, or its layer must make it possible to collide with players.
		#Init the instance. But with collidable set to inverse the class' neverCollides.
		theInst = classDef( self.loc, group=destGroup, collidable=not classDef.neverCollides )


		#Set all the Ghost data onto the new physics objects if applicable.
		if theInst.collidable:
			#First the body
			self.bodyGhost.resurrectOntoGiven( theInst.body )
			#Then the shape.
			self.shapeGhost.resurrectOntoGiven( theInst.shape )
			#Then the sensorBox, if applicable.
		 	if self.sensorGhost is not None:
				self.sensorGhost.resurrectOntoGiven( theInst.sensorBox )


		#Pans
		theInst.oldPan = self.oldPan


		#Set the animation
		theInst.curAnimation = theInst.animations[self.curAnimationName]
		#Set one before the current frame.
		theInst = self.frame - 1
		#Use nextFrame to get to the current frame, and a clean way to make sure the image updates.
		theInst.nextFrame()
		#Now set the correct frameTime.
		theInst.frameTime = self.frameTime

		return theInst
