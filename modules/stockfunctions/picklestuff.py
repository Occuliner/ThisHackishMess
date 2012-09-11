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

import cPickle, os, pygame, zlib, gzip
#import msgpack

from imageload import loadImage, loadImageNoAlpha

#This code is haunted by a SpaceGhost! D:
from physicsserialize import SpaceGhost
from linevisualiser import LineVisualiser

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
	
	#Remove all Surfaces from the playState, for ents, remove them and use the sheetFileName property to reload it later.
	#For the Floor, convert it to a stringbuffer, and make it a property of the floor, and reload it later.

	for eachSprite in givenState.sprites():
		#Create EntityGhosts.
		

	#Create a compressed stringbuffer of the levels floor image.
	floorImageStringBuffer = zlib.compress( pygame.image.tostring( givenState.floor.image, "RGB" ) )


	
	print "Need some sort of sound saving."

	print "HudElemnts still need serialization."
	
	writeObjectToFile( givenState, fileName )

def loadPlayState( fileName, curTileSet ):
	givenState = loadObjectFromFile( fileName )
	if givenState is None:
		print "Map: " + fileName + " does not appear to exist."
		return None
	givenState.forceUpdateEverything = True
	givenState.floor.tileSet = curTileSet

	

	#Create SPACE!
	givenState.space.add_collision_handler( 1, 2, givenState.speshulCaller )
	givenState.space.add_collision_handler( 2, 2, givenState.speshulCaller )

	#Create a boundary body and create the boundaries.

	givenState.lineVisualiser = LineVisualiser( givenState )

	for eachSprite in givenState.sprites():
		#Create entitys.

	givenState.floor.image = pygame.image.fromstring( zlib.decompress( imageStringBuffer ), givenState.floor.size, "RGB" ).convert()

	return givenState
		
