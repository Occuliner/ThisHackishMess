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

import cPickle, os, pygame, zlib, gzip, collections, weakref
#import msgpack

from imageload import loadImage, loadImageNoAlpha

from entityserialize import EntityGhost

from state import PlayState

from floor import Floor

from entity import EntityGroup

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

	#Make the sound State picklable.
	givenState.soundManager.makePicklable()

	#Create the StateStoreTuple, this will store all the data, and be serialized.
	stateTuple = StateStoreTuple( [], floorImageBuffer, givenState.soundManager, [] )

	for eachSprite in givenState.sprites():
		#Create EntityGhost.
		ghost = EntityGhost( eachSprite )
		#Add the the ghost list.
		stateTuple.entityGhostList.append( ghost )

	print "HudElements still need serialization."
	
	writeObjectToFile( stateTuple, fileName )

	#Make the soundState unpicklable
	givenState.soundManager.makeUnpicklable()

	#Set the filename property
	givenState.fileName = fileName

def loadPlayState( fileName, curTileSet, classDefs, networkServer=None, networkClient=None ):
	#Create a new playState
	givenState = PlayState()

	#Create the groups.
	givenState.addGroup( EntityGroup(), name="levelWarpGroup" )
	givenState.addGroup( EntityGroup(), isPlayerGroupBool=True )
	givenState.addGroup( EntityGroup(), name="genericStuffGroup", indexValue=0 )
	if not (networkServer is None):
		givenState.addGroup( EntityGroup( 'networkPlayers' ), name='networkPlayers' )
		givenState.isHost = True
		givenState.networkNode = networkServer
		givenState.networkingStarted = True

	#Create it's floor
	givenState.floor = Floor( curTileSet, ( 800, 608 ) )

	#Get the StateStoreTuple.
	stateTuple = loadObjectFromFile( fileName )
	if stateTuple is None:
		print "No map called: " + fileName + " in the data/maps folder."
		return None

	#Set the amount of ents this file has.
	givenState.amountOfEntsOnLoad = len( stateTuple.entityGhostList )

	#Generate class dict.
	classDefsDict = dict( [ ( eachClass.__name__, eachClass ) for eachClass in classDefs ] )

	#Add all ze entities.
	if not (networkClient is None):
		givenState.networkNode = networkClient
		givenState.networkingStarted = True
		givenState.isClient = True
		for eachGhost in stateTuple.entityGhostList:
			eachGhost.resurrectNetworked( classDefsDict, givenState )
	else:
		for eachGhost in stateTuple.entityGhostList:
			eachGhost.resurrect( classDefsDict, givenState )

	#Replace the floorImage
	givenState.floor.image = pygame.image.fromstring( zlib.decompress( stateTuple.floorImageBuffer.stringBuffer ), stateTuple.floorImageBuffer.size, "RGB" ).convert()

	#Replace the sound manager.
	stateTuple.soundManager.makeUnpicklable()
	givenState.soundManager = stateTuple.soundManager
	givenState.soundManager.playStateRef = weakref.ref( givenState )

	#Set the filename property.
	givenState.fileName = fileName

	return givenState
		
