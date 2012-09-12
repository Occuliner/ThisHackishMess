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

import cPickle, os, pygame, zlib, gzip, collections
#import msgpack

from imageload import loadImage, loadImageNoAlpha

from entityserialize import EntityGhost

from state import PlayState

#This code is haunted by a SpaceGhost! D:
from physicsserialize import SpaceGhost
from linevisualiser import LineVisualiser

StateStoreTuple = collections.namedtuple( "StateStoreTuple", [ "entityGhostList", "floorImageBuffer", "soundManager", "hudElements" ] )

ImageBuffer = collections.namedtuple( "ImageBuffer", [ "size", "stringBuffer" ] )

def writeObjectToFile( obj, fileName ):
	destFile = gzip.open( fileName, 'wb' )
	destFile.write( cPickle.dumps( obj, 2 ) )
	#Msgpack version.
	#destFile.write( msgpack.packb( obj ) )
	destFile.close()
	
def loadObjectFromFile( fileName ):
	if not os.path.isfile( fileName ):
		return None
	theFile = gzip.open( fileName, 'rb' )
	loadString = theFile.read()
	theFile.close()
	#Msgpack version.
	#return msgpack.unpackb( zlib.decompress( loadString ) )
	return cPickle.loads( loadString )
	

def dumpPlayState( givenState, fileName ):
	#Create a compressed stringbuffer of the levels floor image.
	floorImageStringBuffer = zlib.compress( pygame.image.tostring( givenState.floor.image, "RGB" ) )
	#Store it
	floorImageBuffer = ImageBuffer( givenState.floor.size, floorImageStringBuffer )


	#Create the StateStoreTuple, this will store all the data, and be serialized.
	stateTuple = StateStoreTuple( [], floorImageBuffer, None, [] )

	for eachSprite in givenState.sprites():
		#Create EntityGhost.
		ghost = EntityGhost( eachSprite )
		#Add the the ghost list.
		stateTuple.entityGhostList.append( ghost )
		
	print "Need some sort of sound saving."

	print "HudElements still need serialization."
	
	writeObjectToFile( stateTuple, fileName )

def loadPlayState( fileName, curTileSet, classDefs ):
	#Create a new playState
	givenState = PlayState()

	#Give it the newer tileSet.
	givenState.floor.tileSet = curTileSet

	#Get the StateStoreTuple.
	stateTuple = loadObjectFromFile( fileName )
	if stateTuple is None:
		print "No map called: " + fileName + " in the data/maps folder."
		return None

	#Generate class dict.
	classDefsDict = dict( [ ( eachClass.__name__, eachClass ) for eachClass in classDefs ] )

	#Add all ze entities.
	for eachGhost in stateTuple.entityGhostList:
		eachGhost.resurrect( classDefsDict, givenState )

	#Replace the floorImage
	givenState.floor.image = pygame.image.fromstring( zlib.decompress( stateTuple.floorImageBuffer.stringBuffer ), stateTuple.floorImageBuffer.size, "RGB" ).convert()

	return givenState
		
