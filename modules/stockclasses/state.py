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

import pygame, extern_modules.pymunk as pymunk, sys, gc, logging
import extern_modules.pygnetic as pygnetic
#from pygame.locals import *
from linevisualiser import LineVisualiser
from soundmanager import SoundManager
from idsource import IdSource
from networkserver import NetworkServer
from networkclient import NetworkClient
from networkmessages import registerMessages
#from modules.networkents.mindlessentholder import *
from entity import EntityGroup
from modules.gamelogic.manager import ActualManager
from getres import getResolution
from confighandler import ConfigHandler

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
        self.cfg = ConfigHandler( 'thm.cfg' )
        self.cfg.readConfig()
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

        self.gameLogicManager = ActualManager( self )
        self.justEditing = False

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
        self.interweaveOrder={}

        self.curInputDict = {}
        
        self.playersGroup = None

        self.namedGroups = { 'playersGroup':self.playersGroup }

        self.lineVisualiser = LineVisualiser( self )

        self.rerenderEverything = False

        self.soundManager = SoundManager( self )

        self.hudList = []
        
        self.fileName = "Untitled"
        self.amountOfEntsOnLoad = None

        self.hardBlockInput = False
        self.inputDictLog = []

        #These to variables are the displacement from the state's (0,0) and the screen's (0,0), so they can be used for panning.
        self.panX, self.panY = 0, 0
        self.limitX1, self.limitX2, self.limitY1, self.limitY2 = None, None, None, None

        #This is the idSource, I use it for give ids to Entitys.
        self.idSource = IdSource()
    
        self.isClient = False
        self.isHost = False
        self.networkRate = 20.0
        self.networkTicker = 0
        self.networkNode = None
        self.networkingStarted = False

        #This is set by the DevMenu init
        self.devMenuRef = None

        self.paused = False
        self.keyboardInputEnabled = False
        self.deleteLastChar = False
        self.checkFocus = True
        self.pausedByFocus = False

        #So this is quite an important boolean.
        #If this is true everything in the PlayState will be drawn in order of the bottom of it's bounding rect, which I will refer
        #to as 'the foot'. If the foot is higher up the screen, the item will be drawn sooner.
        #If this is False, everything will be drawn according to the drawOrder and interweaveOrder system.
        #DrawByFeet is more suitable for some topdown/isometric games.
        self.drawByFeet = False

        self.useSuggestedGravityEntityPhysics = False

        self.stateToSwap = None

    def initNetworking( self ):
        if not self.networkingStarted:
            #pygnetic.init(logging_lvl=logging.DEBUG)
            pygnetic.init(logging_lvl=logging.ERROR, n_module='socket')
            self.networkingStarted = True
            registerMessages()

    def hostGame( self ):
        if self.isHost:
            del self.networkNode._server
            gc.collect()
        else:
            self.isHost = True
            self.initNetworking()
        self.networkNode = NetworkServer( self, "", int( self.cfg.getVal("port") ), networkingMode=1 )

        self.addGroup( EntityGroup( 'networkPlayers' ), name='networkPlayers' ) 
        print "Beginning hosting..."

    def connectToGame( self, addr, port ):
        if self.isClient:
            del self.networkNode._client
            gc.collect()
        else:
            self.isClient = True
            self.initNetworking()
        self.networkNode = NetworkClient( self, networkingMode=1 )
        self.networkNode.connect( addr, port )

        self.addGroup( EntityGroup( 'networkPlayers' ), name='networkPlayers' ) 
        print "Connecting..."

    def addBoundary( self, point1, point2 ):
        newSeg = pymunk.Segment( self.boundaryBody, point1, point2, 1 )
        self.boundaries.append( newSeg )
        self.space.add( newSeg )

    def removeBoundary( self, givenSeg ):
        self.boundaries.remove( givenSeg )
        self.space.remove( givenSeg )

    def swap( self, newState ):
        self.stateToSwap = newState

    def addInterweaveGroup( self, group, index ):
        if self.interweaveOrder.get( index, None ) is None:
            self.interweaveOrder[index] = [group]
        else:
            self.interweaveOrder[index].append( group )
        
    def addGroup(self, group, indexValue=None, isPlayerGroupBool=False, name=None, interweaveWithFloor=False):
        """Add's an entity group to the PlayState.

        If indexValue specifies the draw-order, defaults to last.
        isPlayerGroupBool specifies if the group is a group of players
        (ie, a group that will be sent input dictionaries).
        If a "name" is given, set PlayState.name = group.
        interweaveWithFloor means that the entityGroup is drawn with 
        the floor layers instead, drawn after the layer of it's index.
        Multiple entgroups can share a interweave number, and they'll be 
        drawn according to order of their addition. an interweave index of 0
        means it will be drawn AFTER layer 1, the first layer above the background floor"""
        
        group.playState = self
        self.groups.append( group )
        if not interweaveWithFloor:
            newIndex = len( self.groups ) - 1
            if indexValue is None:
                self.drawOrder.append( newIndex )
            else:
                self.drawOrder.insert( indexValue, newIndex )
        else:
            newIndex = len( self.floor.layers ) - 1
            if indexValue is None:
                self.addInterweaveGroup( group, newIndex )
            else:
                self.addInterweaveGroup( group, indexValue )
        
        if isPlayerGroupBool:
            self.namedGroups['playersGroup'] = group
            self.playersGroup = group
        
        if name is not None:
            self.namedGroups[name] = group
            setattr( self, name, group )

    def checkForFocus( self ):
        lostFocus = ( not pygame.mouse.get_focused() ) and self.checkFocus
        self.pausedByFocus = lostFocus

    def pause( self ):
        self.paused = True

    def unpause( self ):
        self.paused = False

    def togglePaused( self ):
        self.paused = not self.paused

    def processNetworkEvents( self, dt ):
        self.gameLogicManager.preNetworkTick( dt )
        if self.isHost or self.isClient:
            if self.networkTicker >= int(60.0/self.networkRate):
                self.networkNode.update( dt )
                self.networkTicker = -1
            self.networkNode.updateTime( dt )
            self.networkTicker += 1
        self.gameLogicManager.postNetworkTick( dt )

    def update( self, dt ):
        """A generic update function.
        Sends input dictionaries to playerGroups.
        Updates all the child groups, runs the collision system."""
        
        self.floor.update( self.panX, self.panY )
        
        self.checkForFocus()
        if self.paused or self.pausedByFocus:
            self.processNetworkEvents( dt )
            return None

        #Game logic
        self.gameLogicManager.preTick( dt )

        if not self.hardBlockInput:
            #I'm doing the same thing even if the host or client is the same, to force identical player behaviour for either.
            if self.isClient or self.isHost:
                self.inputDictLog.append( self.curInputDict )
                if self.networkTicker >= int(60.0/self.networkRate):
                    for eachDict in self.inputDictLog:
                        if self.playersGroup is not None and len( eachDict ) > 0:
                            for eachPlayer in self.playersGroup.sprites():
                                eachPlayer.sendInput( eachDict )
                    
                        for eachElement in self.hudList:
                            eachElement.sendInput( eachDict )
                    self.inputDictLog = []
                if self.isClient:
                    self.networkNode.sendInput( self.curInputDict )
            else:
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
        self.processNetworkEvents( dt )
        self.gameLogicManager.postTick( dt )

    def setPan( self, x, y ):
        screenW, screenH = getResolution()
        if self.limitX1 is not None:
            x = min( -self.limitX1, x )
        if self.limitX2 is not None:
            x = max( -(self.limitX2-screenW), x )
        if self.limitY1 is not None:
            y = min( -(self.limitY1), y )
        if self.limitY2 is not None:
            y = max( -(self.limitY2-screenH), y )
        self.panX, self.panY = x, y

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

        changeRects.append( surface.blit( self.floor.layers[0].image, self.floor.layers[0].rect.topleft ) )
        if not self.drawByFeet:
            for eachVal in self.drawOrder:
                changeRects.extend( self.groups[eachVal].draw( surface ) )

            allInterweaveGroups = self.interweaveOrder.values()
            for eachVal in range( 1, len( self.floor.layers ) ):
                eachLayer = self.floor.layers[eachVal]            
                changeRects.append( surface.blit( eachLayer.image, eachLayer.rect.topleft ) )
                groupsToDraw = self.interweaveOrder.get( eachVal-1, None )
                if groupsToDraw is not None:
                    allInterweaveGroups.remove( groupsToDraw )
                    [ changeRects.extend( each.draw( surface ) ) for each in groupsToDraw ]
            #Draw anything left over
            for eachGroupSet in allInterweaveGroups:
                [ changeRects.extend( eachGroup.draw( surface ) ) for eachGroup in eachGroupSet ]

        else:
            yTuples = []
            for eachSprite in self.sprites():
                if eachSprite.flatInDrawByFeet:
                    y = eachSprite.rect.top
                else:
                    y = eachSprite.rect.bottom
                yTuples.append( (y, eachSprite) )
            yTuples.extend( [ (each.rect.bottom, each) for each in self.floor.layers[1:] ] )

            renderList = [ each[1] for each in sorted( yTuples, lambda x, y: cmp( x[0], y[0] ) ) ]
            #I probably shouldn't be doing this.
            tmpDrawGroup = pygame.sprite.LayeredDirty( self.floor.layers[0], renderList )
            changeRects.extend( tmpDrawGroup.draw( surface ) )
            tmpDrawGroup.empty()
            del tmpDrawGroup
        
        changeRects.extend( self.lineVisualiser.draw( surface, (self.panX, self.panY) ) )

        for eachElement in self.hudList:
            eachElement.draw( surface )

        changeRects.extend( [ each.rect for each in self.hudList ] )
        
        if self.rerenderEverything:
            w, h = surface.get_width(), surface.get_height()
            changeRects.extend( [ pygame.Rect( 0, 0, w, h ) ] )
            self.rerenderEverything = False
        return changeRects

    #
    #
    #    This function, __getitem__, takes a value, if that value is a string, it looks for a group in PlayState.groups that has that string as entityGroup.name.
    #    If that value is an int, it returns the group at that index value in self.groups.
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
