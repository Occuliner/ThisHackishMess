# Copyright (c) 2013 Connor Sherson
#
# This software is provided 'as-is', without any express or implied
# warranty. In no event will the authors be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
#    1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
#
#    2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
#
#    3. This notice may not be removed or altered from any source
#    distribution.

"""This module contains the pre-processer class for creating simple representations of Entity objects for use with serialization."""
import pygame, copy

from physicsserialize import *

class EntityGhost:
    """This is a Ghost for Entity types.
    Really, it only specifies things that aren't automatically created by the class' __init__.
    That's just entity location, animation details (Current animation, frame time counters etc), references to the Entitie's physics-objects, the Entities's children entities, its tags, oldPan data, and any instance specific data the system can identify."""
    def __init__( self, theEntity ):
        #Grab the class name of the Entity.
        self.className = theEntity.__class__.__name__

        self.id = theEntity.id
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

        self.collidable = theEntity.collidable

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


        ## INSTANCE SPECIFIC 

        #Create an empty dict to hold them all.
        self.instanceSpecificVars = {}
        #Iterate over the vars.
        for eachKey, eachVal in theEntity.instanceSpecificVars.items():
            #Get the type string.
            typeString = str( type(eachVal) )


            #Make sure it's not in the pygame or pygnetic modules
            if 'pygame' in typeString or 'pygnetic' in typeString:
                #Raise an exception in this scenario.
                raise Exception( "You appear to be trying to seralize an Entity of type " + str( type( theEntity ) ) + 
                    "with a pygame-class or pygnetic-class instanceSpecificVarible, " + eachKey + ", of type " + typeString +
                    " .The serializer will never do this for you to avoid license issues with the LGPL Pygame and Pygnetic." +
                    " You should consider adding serialization support for this class type to the entity serialize module." )
            else:
                #Otherwise, assume it's safe to add
                #self.instanceSpecificVars[eachKey] = eachVal
                self.instanceSpecificVars[eachKey] = copy.deepcopy(theEntity.__dict__[eachKey])

        #Get the Entity rotation.
        self.angle = theEntity.angle

        ## CHILDREN STUFF

        #Turn the children into ghosts.
        self.childrenGhosts = [ EntityGhost( each ) for each in theEntity.children ]

	#Get the childrens' ids.
        self.childrenIds = [ each.id for each in theEntity.children ]

    def resurrect( self, classDefs, playState ):
        """This is the standard resurrect function. It takes a dict of ClassName:Class for finding the right constructor to call,
         and the playState as parameters."""

        #PUT TESTS FOR SUPPORTED SERIALIZABLE PYGAME FORMATS. Such as Surfaces.

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
        theInst.frame = self.frame - 1
        #Use nextFrame to get to the current frame, and a clean way to make sure the image updates.
        theInst.nextFrame()
        #Now set the correct frameTime.
        theInst.frameTime = self.frameTime

	#Rotate
        theInst.setRotation( self.angle )

        #Now set the instance specific vars.
        for eachKey, eachVal in self.instanceSpecificVars.items():
            setattr( theInst, eachKey, eachVal )

	#Now recreate the children.
        theInst.children = [ each.resurrect( classDefs, playState ) for each in self.childrenGhosts ]

        return theInst

    def resurrectNetworked( self, classDefs, playState ):
        """This is the networked resurrect function. It creates network-entities.
        It takes a dict of ClassName:Class for finding the right constructor to call,
        and the playState as parameters."""
        #Set the animation
        theInst.curAnimation = theInst.animations[self.curAnimationName]
        #Set one before the current frame.
        theInst.frame = self.frame - 1
        #Use nextFrame to get to the current frame, and a clean way to make sure the image updates.
        theInst.nextFrame()
        #Now set the correct frameTime.
        theInst.frameTime = self.frameTime

        #Get the appropriate class def.
        if "Network" in self.className:
            classDef = classDefs[self.className]
        else:
            classDef = classDefs[self.className+"Network"]
        
        #Get the dest group.
        destGroup = getattr( playState, classDef.playStateGroup )


        #TO DO! Make it so that an object must either be set to neverCollides, or its layer must make it possible to collide with players.
        #Init the instance. But with collidable set to inverse the class' neverCollides.
        #theInst = classDef( self.loc, group=destGroup, collidable=not classDef.neverCollides )
        theInst = classDef( self.loc, group=destGroup )#, forceId=self.id )

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
        theInst.frame = self.frame - 1
        #Use nextFrame to get to the current frame, and a clean way to make sure the image updates.
        theInst.nextFrame()
        #Now set the correct frameTime.
        theInst.frameTime = self.frameTime
        #Set the id
        theInst.id = self.id

        #Now set the instance specific vars.
        for eachKey, eachVal in self.instanceSpecificVars.items():
            setattr( theInst, eachKey, eachVal )

        #Rotate
        theInst.setRotation( self.angle )

        #Now recreate the children.
        theInst.children = [ each.resurrectNetworked( classDefs, playState ) for each in self.childrenGhosts ]
        return theInst
