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

import cPickle, os, pygame, zlib, gzip, collections, weakref, state, sys
#import msgpack

from imageload import loadImage, loadImageNoAlpha

from entityserialize import EntityGhost

from floor import Floor, FloorLayer

from entity import EntityGroup

#This code is haunted by a SpaceGhost! D:
from physicsserialize import SpaceGhost
from linevisualiser import LineVisualiser

StateStoreTuple = collections.namedtuple( "StateStoreTuple", [ "entityGhostList", "floorImageBuffers", "soundManager", "hudElements", "boundaries" ] )

ImageBuffer = collections.namedtuple( "ImageBuffer", [ "size", "stringBuffer" ] )

def makeImageBuffer( image ):
    #Create a compressed stringbuffer of the levels floor image.
    floorImageStringBuffer = zlib.compress( pygame.image.tostring( image, "RGBA" ) )
    #Store it
    return ImageBuffer( (image.get_width(), image.get_height()), floorImageStringBuffer )

def makeImageFromBuffer( imgBuffer ):
    return pygame.image.fromstring( zlib.decompress( imgBuffer.stringBuffer ), imgBuffer.size, "RGBA" ).convert_alpha()

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
    

def dumpPlayState( givenState, fileName, saveHud=False ):
    #To avoid crashers of anykind when saving. Everything is in a try block.
    try:
        #Store all the Floor layers.
        floorImageBuffers = [ ( makeImageBuffer( each.image ), each.rect.topleft ) for each in givenState.floor.layers ]

        #Make the sound State picklable.
        givenState.soundManager.makePicklable()
    
        #Make a list representing all the boundaries.
        bndList = [ ( (each.a.x, each.a.y), (each.b.x, each.b.y) ) for each in givenState.boundaries ]
    
        if saveHud:
            #Make the hudElements picklable.
            hudList = [ each.makePicklable() for each in givenState.hudList ]
        else:
            hudList = []
    
        #Create the StateStoreTuple, this will store all the data, and be serialized.
        stateTuple = StateStoreTuple( [], floorImageBuffers, givenState.soundManager, hudList, bndList )
    
        for eachSprite in givenState.sprites():
            #Create EntityGhost.
            ghost = EntityGhost( eachSprite )
            #Add the the ghost list.
            stateTuple.entityGhostList.append( ghost )
    
        
        writeObjectToFile( stateTuple, fileName )
        
        #Make the soundState unpicklable
        givenState.soundManager.makeUnpicklable( givenState )
    
        if saveHud:
            #Make the hud elements unpicklable
            [ each.makeUnpicklable( givenState ) for each in givenState.hudList ]
    
        #Set the filename property
        givenState.fileName = fileName

    except:
        print "Saving failed apparently: " + sys.exc_info()[0]

        #I think it's safe to just unpicklablize the sounds and hud elements, even if some aren't picklable.
        
        #Make the soundState unpicklable
        givenState.soundManager.makeUnpicklable( givenState )
    
        if saveHud:
            #Make the hud elements unpicklable
            [ each.makeUnpicklable( givenState ) for each in givenState.hudList ]

        

def loadPlayState( fileName, curTileSet, classDefs, networkServer=None, networkClient=None, loadHud=False ):
    #Get the StateStoreTuple.
    stateTuple = loadObjectFromFile( fileName )
    if stateTuple is None:
        print "No map called: " + fileName + " in the data/maps folder."
        return None

    #Create a new playState
    givenState = state.PlayState()

    #Create the groups.
    givenState.addGroup( EntityGroup(), name="levelWarpGroup" )
    givenState.addGroup( EntityGroup(), isPlayerGroupBool=True )
    givenState.addGroup( EntityGroup(), name="genericStuffGroup", indexValue=0 )
    if not (networkServer is None):
        givenState.addGroup( EntityGroup( 'networkPlayers' ), name='networkPlayers' )
        givenState.isHost = True
        givenState.networkNode = networkServer
        givenState.networkingStarted = True
        networkSever.playStateRef = weakref.ref( givenState )

    #Create it's floor
    givenState.floor = Floor( curTileSet, ( 800, 608 ) )

    #Set the amount of ents this file has.
    givenState.amountOfEntsOnLoad = len( stateTuple.entityGhostList )

    #Generate class dict.
    classDefsDict = dict( [ ( eachClass.__name__, eachClass ) for eachClass in classDefs ] )

    #Add all ze entities.
    if not (networkClient is None):
        givenState.networkNode = networkClient
        givenState.networkingStarted = True
        givenState.isClient = True
        networkClient.playStateRef = weakref.ref( givenState )
        for eachGhost in stateTuple.entityGhostList:
            eachGhost.resurrectNetworked( classDefsDict, givenState )
    else:
        for eachGhost in stateTuple.entityGhostList:
            eachGhost.resurrect( classDefsDict, givenState )

    #Replace the floor layers.
    givenState.floor.layers = [ FloorLayer( pos=each[1], image=makeImageFromBuffer( each[0] ) ) for each in stateTuple.floorImageBuffers ]

    #Replace the sound manager.
    stateTuple.soundManager.makeUnpicklable( givenState )
    givenState.soundManager = stateTuple.soundManager
    givenState.soundManager.playStateRef = weakref.ref( givenState )

    #Set the filename property.
    givenState.fileName = fileName

    #Add the boundaries.
    [ givenState.addBoundary( each[0], each[1] ) for each in stateTuple.boundaries ]

    if loadHud:
        #Make the hud elements unpicklable, then add them.
        [ each.makeUnpicklable( givenState ) for each in stateTuple.hudElements ]
        givenState.hudList = stateTuple.hudElements

    return givenState
        
