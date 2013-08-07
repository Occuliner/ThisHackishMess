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

from entity import Entity
import pygame, os
from imageload import loadImage, loadImageNoAlpha

from masterentityset import *

from picklestuff import *

def levelWarpFunc( givenWarp, givenObject ):
    curPlayState = givenObject.groups()[0].playState
    if givenObject in curPlayState.playersGroup:
        givenWarp.collidedWith.add( givenObject.id )
        if givenObject not in givenWarp.ignore:
            dest = loadPlayState( os.path.join( "data", "maps", givenWarp.tags["warpDest"] ), curPlayState.floor.tileSet )
            if dest is None:
                return None
            targetWarp = None
            for each in dest.levelWarpGroup:
                if each.tags.get("warpKey") == givenWarp.tags["warpKey"]:
                    targetWarp = each
                    break
            if targetWarp is None:
                print "No levelWarp with warpKey: " + givenWarp.tags["warpKey"] + " appears to exist in the destination map."
                return None
            givenObject.removeFromGroup( curPlayState.playersGroup )
            for each in givenObject.children:
                each.removeFromGroup( curPlayState.playersGroup )
            givenObject.body.position = targetWarp.body.position.x, targetWarp.body.position.y
            curPlayState.swap( dest )
            givenObject.addToGroup( curPlayState.playersGroup )
            for each in givenObject.children:
                each.addToGroup( curPlayState.playersGroup )
            targetWarp.ignore.add( givenObject.id )
            targetWarp.collidedWith.add( givenObject.id )
            curPlayState.rerenderEverything = True

def queueLoad( givenWarp, givenObject ):
    curPlayState = givenObject.groups()[0].playState
    curPlayState.postStepQueue.append( ( levelWarpFunc, givenWarp, givenObject ) )

class LevelWarp( Entity ):

    scale = 2 
    
    width = 16
    height = 16

    playStateGroup = "levelWarpGroup"
    setName = "levelwarp"

    sheetFileName = "block.png"
    sheet = loadImage( sheetFileName, scale )

    specialCollision = queueLoad
    collidable = True
    solid = False
    mass = 20

    instanceSpecificVars = None
    
    def __init__( self, pos = [0,0], vel = [0,0], group=None, **kwargs ):
        Entity.__init__( self, pos, [0,0], None, group, pygame.Rect( 0, 0, self.width, self.height ), animated=False, **kwargs )
        if LevelWarp.instanceSpecificVars is None:
            attrList = list( self.__dict__.keys() )

        #self.shape.collision_type = 1
        self.tags["warpKey"] = "prime"
        self.tags["warpDest"] = "testthingy"
        self.ignore = set([])
        self.collidedWith = set([])

        if LevelWarp.instanceSpecificVars is None:
            LevelWarp.instanceSpecificVars = dict( [ ( eachKey, eachVal ) for eachKey, eachVal in self.__dict__.items() if eachKey not in attrList ] )
    
    def update( self, dt ):
        Entity.update( self, dt )
        for each in self.groups()[0].playState.playersGroup:
            if each.id not in self.collidedWith and each.id in self.ignore:
                self.ignore.remove( each.id )
        self.collidedWith = set([])
        

#MasterEntitySet.entsToLoad.append( LevelWarp )
entities = { "LevelWarp":LevelWarp }
