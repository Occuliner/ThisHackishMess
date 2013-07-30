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

"""This script is the launcher for the ThisHackishMess gamebase/devkit.
It creates the window, DevMenu, basic playState, an empty playerGroup.
It then runs the main-loop. Rendering everything in the playState and 
sending a dictionary of key inputs to the playerGroup in the playState."""

import pygame, weakref, sys#, objgraph

#from pygame.locals import QUIT, KEYDOWN, K_UP, K_LEFT, K_RIGHT, K_DOWN, K_RETURN, KEYUP, MOUSEBUTTONDOWN, MOUSEBUTTONUP

from pygame.locals import *

pygame.init()

#Apparently all the scripts ran by extention of this have this in their paths, huh.
sys.path.extend( ["modules/stockfunctions", "modules/stockclasses", "extern_modules"] )

from entity import EntityGroup

from floor import Floor

from devtools import DevMenu

from state import PlayState

from confighandler import ConfigHandler

cfg = ConfigHandler( 'thm.cfg' )
cfg.readConfig()

#from modules import *

timer = pygame.time.Clock()

if int(cfg.getVal('fullscreen')) == 1:
    screen = pygame.display.set_mode( (cfg.getWidth(), cfg.getHeight()), pygame.FULLSCREEN )
else:
    screen = pygame.display.set_mode( (cfg.getWidth(), cfg.getHeight()) )

#pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP])

pygame.display.set_caption( cfg.getVal('caption') )#'ThisHackishMess' )

done = False

black = pygame.Color( 0, 0, 0 )

#
#    Set Up the PlayState!
#

currentState = PlayState()

#
#    This import seems pointless, but without there won't actually be any 
#    tiles placed in MasterTileSet, causing the Floor() call later to fail.
#
from modules.tilesets.devtileset import DevDraftSet

from modules.tilesets.mastertileset import MasterTileSet

prototypeTileGroup = MasterTileSet()

playArea = Floor( prototypeTileGroup, (cfg.getWidth(), cfg.getHeight()) )

currentState.floor = playArea


#Create EntityGroups!

playerGroup = EntityGroup()

genericStuffGroup = EntityGroup()

levelWarpGroup = EntityGroup()

currentState.addGroup( levelWarpGroup, name="levelWarpGroup" )

currentState.addGroup( playerGroup, isPlayerGroupBool=True )

currentState.addGroup( genericStuffGroup, name="genericStuffGroup", indexValue=0 )

devMode = cfg.getVal('dev_mode') == "1"

#Make the dev menu
theDevMenu = DevMenu( currentState, devMode )

#Delete a lot of unneeded stuff.
del levelWarpGroup, playerGroup, genericStuffGroup, playArea, DevDraftSet, MasterTileSet, prototypeTileGroup

#This dict is a dict of all the key events.

inputDict = {}

shiftHeld = False

timeTillFpsPrint = 2.0

updatedArea = [ pygame.Rect( 0, 0, cfg.getWidth(), cfg.getHeight() ) ]

panU, panD, panL, panR = False, False, False, False

#Game logic.
currentState.gameLogicManager.onLaunch()

#
#
#    Game Loop!
#
#

timer.tick( 60 )
while not done:

    screen.fill( black )

    currentState.update( float(timer.get_time())/1000 )

    updatedArea.extend( currentState.draw( screen ) )
    
    theDevMenu.update( float(timer.get_time())/1000 )
    updatedArea.extend( theDevMenu.draw( screen ) )


    for event in pygame.event.get():
        if event.type == QUIT:
            if currentState.isHost or currentState.isClient:
                currentState.networkNode.disconnectAll()
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if theDevMenu.menuState.keyboardEnabled:
                someChr = event.unicode
                if chr(8) == someChr:
                    theDevMenu.menuState.deleteLastChar = True
                else:
                    theDevMenu.menuState.keyboardInput( someChr )
            if currentState.keyboardInputEnabled:
                someChr = event.unicode
                if chr(8) == someChr:
                    currentState.deleteLastChar = True
                else:
                    for eachEl in currentState.hudList:
                        eachEl.keyboardInput( someChr )
            elif event.key == K_UP:
                inputDict['K_UP'] = 'down'
            elif event.key == K_LEFT:
                inputDict['K_LEFT'] = 'down'
            elif event.key == K_RIGHT:
                inputDict['K_RIGHT'] = 'down'
            elif event.key == K_DOWN:
                inputDict['K_DOWN'] = 'down'
            elif event.key == K_TAB:
                
                if devMode:
                    #OPEN PANEL
                    theDevMenu.toggle()

            elif event.key in [ K_LSHIFT, K_RSHIFT ]:
                shiftHeld = True
            elif event.key == K_w and shiftHeld and theDevMenu.open:
                panU = True
            elif event.key == K_a and shiftHeld and theDevMenu.open:
                panL = True
            elif event.key == K_d and shiftHeld and theDevMenu.open:
                panR = True
            elif event.key == K_s and shiftHeld and theDevMenu.open:
                panD = True
            
        elif event.type == KEYUP:
            if event.key == K_LEFT:
                inputDict['K_LEFT'] = 'up'
            elif event.key == K_RIGHT:
                inputDict['K_RIGHT'] = 'up'
            elif event.key == K_UP:
                inputDict['K_UP'] = 'up'
            elif event.key == K_DOWN:
                inputDict['K_DOWN'] = 'up'
            elif event.key in [ K_LSHIFT, K_RSHIFT ]:
                shiftHeld = False
            elif event.key == K_w:
                panU = False
            elif event.key == K_a:
                panL = False
            elif event.key == K_d:
                panR = False
            elif event.key == K_s:
                panD = False
            elif event.key == K_ESCAPE:
                currentState.togglePaused()
            
        elif event.type == MOUSEBUTTONDOWN:
            curMousePos = event.pos[0] + currentState.panX, event.pos[1] + currentState.panY
            if event.button == 1 and theDevMenu.open:
                theDevMenu.clicks['mouse1down'].append( event.pos )
            elif event.button == 2 and theDevMenu.open:
                theDevMenu.clicks['mouse2down'].append( event.pos )
            elif event.button == 3 and theDevMenu.open:
                theDevMenu.clicks['mouse3down'].append( event.pos )
        
        elif event.type == MOUSEBUTTONUP:
            theDevMenu.draggingMenu = False
            theDevMenu.draggedSpot = [0,0]
            curMousePos = event.pos[0] + currentState.panX, event.pos[1] + currentState.panY
            if event.button == 1 and theDevMenu.open:
                theDevMenu.clicks['mouse1up'].append( event.pos )
            elif event.button == 2 and theDevMenu.open:
                theDevMenu.clicks['mouse2up'].append( event.pos )
            elif event.button == 3 and theDevMenu.open:
                theDevMenu.clicks['mouse3up'].append( event.pos )

    currentState.sendInput( inputDict )
    
    inputDict = {}
    
    if panU:
        currentState.setPan( currentState.panX, currentState.panY + 2 )
    if panD:
        currentState.setPan( currentState.panX, currentState.panY - 2 )
    if panR:
        currentState.setPan( currentState.panX - 2, currentState.panY)
    if panL:
        currentState.setPan( currentState.panX + 2, currentState.panY )

    #pygame.display.update( updatedArea )
    pygame.display.update( )

    updatedArea = []

    if currentState.stateToSwap is not None:
        currentState = currentState.stateToSwap
        theDevMenu.playState = currentState
        currentState.devMenuRef = weakref.ref( theDevMenu )
        #Call game logic events.
        currentState.gameLogicManager.onLoad()

    timeTillFpsPrint -= float(timer.get_time())/1000
    if timeTillFpsPrint < 0:
        print timer.get_fps()
        timeTillFpsPrint = 2.0
    timer.tick( 60 )
