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

#import modules.entitysets

class EntityGhost:
	"""This is a Ghost for Entity types."""
	"""Really, it only specifies things that aren't automatically created by the class' __init__."""
	"""That's just rect loc, animation details (Current animation, frame time counters etc), references to the Entitie's physics-objects, the Entities's children entities, its tags, oldPan data, and any instance specific data the system can identify."""
	def __init__( self, theEntity ):


		## ANIMATION STUFF

		#Grab the current anim.
		self.curAnimation = theEntity.curAnimation
		#Grab the current frame
		self.frame = theEntity.frame
		#Grab the current frameTime
		self.frameTime = theEntity.frameTime
		

		## PAN STUFF Grab the oldPans.
		self.oldPan = theEntity.oldPans


		## TAGS STUFF Grab the tags.
		self.tags = theEntity.tags


		## RECT STUFF Grab the rectloc.
		self.rectLoc = theEntity.rect.topleft


		## PHYSICS STUFF

		#Get the id of everything in the physics object list.
		self.physicsObjectIds = [ id( each ) for each in theEntity.physicsObjects ]
		#Get the id of the body.
		self.bodyId = theEntity.bodyId
		#Get the id of shape.
		self.shapeId = theEntity.shapeId
		#Get the id of the sensorBox, if it's there.
		self.sensorId = getattr( theEntity, "sensorId", None )
		

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
