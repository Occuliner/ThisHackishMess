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

import cPickle
#import msgpack
import pygame
import zlib, random

from imageload import loadImage

#This code is haunted by a SpaceGhost! D:
from physicsserialize import SpaceGhost
from linevisualiser import LineVisualiser

def writeObjectToFile( obj, fileName ):
	#cPickle.dump( obj, file( fileName, "w" ), 2 )
	destFile = open( fileName, "w" )
	destFile.write( zlib.compress( cPickle.dumps( obj, 2 ) ) )
	#Msgpack version.
	#destFile.write( zlib.compress( msgpack.packb( obj ) ) )
	destFile.close()
	
def loadObjectFromFile( fileName ):
	#return cPickle.load( file( fileName, "r" ) )
	theFile = open( fileName, "r" )
	loadString = theFile.read()
	theFile.close()
	#Msgpack version.
	#return msgpack.unpackb( zlib.decompress( loadString ) )
	return cPickle.loads( zlib.decompress( loadString ) )
	

def dumpPlayState( givenState, fileName ):
	#objgraph.show_most_common_types(limit=20)
	#statePickler = cPickle.Pickler( file( fileName, "w" ), 2 )
	
	#Remove all Surfaces from the playState, for ents, remove them and use the sheetFileName property to reload it later.
	#For the Floor, convert it to a stringbuffer, and make it a property of the floor, and reload it later.
	allTheImages = {}
	allTheEntBodies = {}
	allTheEntShapes = {}
	for eachSprite in givenState.sprites():
		allTheImages[id(eachSprite)] = [ eachSprite.sheet, eachSprite.image, eachSprite.frames ]
		eachSprite.image = None
		eachSprite.sheet = None
		eachSprite.frames = []
		if eachSprite.collidable:
			allTheEntBodies[eachSprite.bodyId] = eachSprite.body
			allTheEntShapes[eachSprite.shapeId] = eachSprite.shape
			eachSprite.body = None
			eachSprite.shape = None
			eachSprite.physicsObjects = []
		
	floorImage = givenState.floor.image
	#givenState.floor.imageStringBuffer = pygame.image.tostring( givenState.floor.image, "RGB" )
	givenState.floor.imageStringBuffer = zlib.compress( pygame.image.tostring( givenState.floor.image, "RGB" ) )
	
	givenState.floor.image = None

	backupChanges, backupUndoneChanges, backUpTileSet = givenState.floor.changes, givenState.floor.undoneChanges, givenState.floor.tileSet
	givenState.floor.changes, givenState.floor.undoneChanges, givenState.floor.tileSet = [], [], None

	oldSpace, oldVis, oldBoundaries, oldBoundaryBody = givenState.space, givenState.lineVisualiser, givenState.boundaries, givenState.boundaryBody

	#damnVis = givenState.lineVisualiser
	#oldRenderLines, oldRenderPhysicsLines, oldForceNoRender = damnVis.renderLines, damnVis.renderPhysicsLines, damnVis.forceNoRender
	#givenState.lineVisualiser.renderLines, givenState.lineVisualiser.renderPhysicsLines, givenState.lineVisualiser.forceNoRender = False, False, False

	givenState.spaceGhost = SpaceGhost( givenState.space, givenState.boundaryBody )

	givenState.space, givenState.lineVisualiser, givenState.boundaryBody, givenState.boundaries = None, None, id( givenState.boundaryBody ), [ id( each ) for each in givenState.boundaries ]
	
	writeObjectToFile( givenState, fileName )

	givenState.space, givenState.lineVisualiser, givenState.boundaries, givenState.boundaryBody = oldSpace, oldVis, oldBoundaries, oldBoundaryBody
	#givenState.lineVisualiser.renderLines, givenState.lineVisualiser.renderPhysicsLines, givenState.lineVisualiser.forceNoRender = oldRenderLines, oldRenderPhysicsLines, oldForceNoRender

	#print len( givenState.sprites() )
	for eachSprite in givenState.sprites():
		stuffList = allTheImages[id(eachSprite)]
		eachSprite.sheet = stuffList[0]
		eachSprite.image = stuffList[1]
		eachSprite.frames = stuffList[2]
		if eachSprite.collidable:
			eachSprite.body = allTheEntBodies[eachSprite.bodyId]
			eachSprite.shape = allTheEntShapes[eachSprite.shapeId]
			eachSprite.physicsObjects = [ eachSprite.body, eachSprite.shape ]

	givenState.floor.image = floorImage
	givenState.floor.changes, givenState.floor.undoneChanges, givenState.floor.tileSet = backupChanges, backupUndoneChanges, backUpTileSet

def loadPlayState( fileName, curTileSet ):
	givenState = loadObjectFromFile( fileName )
	givenState.forceUpdateEverything = True
	givenState.floor.tileSet = curTileSet

	givenState.space, bodyDict, shapeDict = givenState.spaceGhost.resurrect()
	givenState.spaceGhost = None
	givenState.space.add_collision_handler( 1, 2, givenState.speshulCaller )
	givenState.space.add_collision_handler( 2, 2, givenState.speshulCaller )

	givenState.boundaryBody = bodyDict[givenState.boundaryBody]
	givenState.boundaries = [ shapeDict[each] for each in givenState.boundaries ]

	givenState.lineVisualiser = LineVisualiser( givenState )

	for eachSprite in givenState.sprites():
		eachSprite.sheet = loadImage( eachSprite.sheetFileName )
		eachSprite.createFrames()
		eachSprite.image = eachSprite.frames[eachSprite.curAnimation['frames'][eachSprite.frame]]
		if hasattr( eachSprite, "baseSheet" ):
			eachSprite.baseSheet = eachSprite.sheet.copy()
		if eachSprite.collidable:
			eachSprite.body = bodyDict[eachSprite.bodyId]
			eachSprite.shape = shapeDict[eachSprite.shapeId]
			eachSprite.shape.entity = eachSprite
			eachSprite.physicsObjects = [ eachSprite.body, eachSprite.shape ]
			eachSprite.body.velocity_func = eachSprite.velocity_func
			eachSprite.bodyId, eachSprite.shapeId = id( eachSprite.body ), id( eachSprite.shape )
	#givenState.floor.image = pygame.image.fromstring( givenState.floor.imageStringBuffer, givenState.floor.size, "RGB" )
	givenState.floor.image = pygame.image.fromstring( zlib.decompress( givenState.floor.imageStringBuffer ), givenState.floor.size, "RGB" ).convert()

	givenState.floor.imageStringBuffer = None
	
	#objgraph.show_most_common_types()
	#obj = objgraph.by_type('list')[-1]
	#objgraph.show_backrefs([obj], max_depth=10)
	#objgraph.show_backrefs( objgraph.by_type('list')[-1] )
	return givenState
		
