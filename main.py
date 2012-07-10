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

"""This script is the launcher for the ThisHackishMess gamebase/devkit.
It creates the window, DevMenu, basic playState, an empty playerGroup.
It then runs the main-loop. Rendering everything in the playState and 
sending a dictionary of key inputs to the playerGroup in the playState."""

import pygame, sys#, objgraph

#from pygame.locals import QUIT, KEYDOWN, K_UP, K_LEFT, K_RIGHT, K_DOWN, K_RETURN, KEYUP, MOUSEBUTTONDOWN, MOUSEBUTTONUP

from pygame.locals import *

pygame.init()

#Apparently all the scripts ran by extention of this have this in their paths, huh.
sys.path.extend( ["modules/stockfunctions", "modules/stockclasses"] )

from entity import EntityGroup

from floor import Floor

from devtools import DevMenu

from state import PlayState

#from modules import *

timer = pygame.time.Clock()

screen = pygame.display.set_mode( (800, 600) )

#pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP])

pygame.display.set_caption( 'ThisHackishMess' )

done = False

white = pygame.Color( 255, 255, 255 )

#
#	Set Up the PlayState!
#

currentState = PlayState()

playerGroup = EntityGroup()

genericStuffGroup = EntityGroup()

#theYasb = YasbClass( yasbGroup )

levelWarpGroup = EntityGroup()

currentState.addGroup( levelWarpGroup, name="levelWarpGroup" )

currentState.addGroup( playerGroup, isPlayerGroupBool=True )

currentState.addGroup( genericStuffGroup, name="genericStuffGroup", indexValue=0 )

#
#	This import seems pointless, but without there won't actually be any 
#	tiles placed in MasterTileSet, causing the Floor() call later to fail.
#
from modules.tilesets.testtileset import TestTileSet

from modules.tilesets.mastertileset import MasterTileSet

prototypeTileGroup = MasterTileSet()

#prototypeTileGroup.addSet( TestTileSet() )
#prototypeTileGroup.updateSets()

playArea = Floor( prototypeTileGroup, ( 800, 608 ) )

currentState.floor = playArea

theDevMenu = DevMenu( currentState )


#
#
#	Game Loop!
#
#

#This dict is a dict of all the key events.

del levelWarpGroup, playerGroup, genericStuffGroup, playArea, TestTileSet, MasterTileSet, prototypeTileGroup

inputDict = {}

shiftHeld = False

timeTillFpsPrint = 2.0

updatedArea = [ pygame.Rect( 0, 0, 800, 600 ) ]
timer.tick( 60 )
while not done:

	screen.fill( white )

	currentState.update( float(timer.get_time())/1000 )

	updatedArea.extend( currentState.draw( screen ) )
	
	theDevMenu.update( float(timer.get_time())/1000 )
	updatedArea.extend( theDevMenu.draw( screen ) )


	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
		elif event.type == KEYDOWN:
			if event.key == K_UP:
				inputDict['K_UP'] = 'down'
			elif event.key == K_LEFT:
				inputDict['K_LEFT'] = 'down'
			elif event.key == K_RIGHT:
				inputDict['K_RIGHT'] = 'down'
			elif event.key == K_DOWN:
				inputDict['K_DOWN'] = 'down'
			elif event.key == K_TAB:
				
				#OPEN PANEL
				
				theDevMenu.toggle()	
				#pass

				#theYasb.nextFrame()

			elif event.key in [ K_LSHIFT, K_RSHIFT ]:
				shiftHeld = True
			
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
			elif event.key == K_BACKSPACE:
				#objgraph.show_most_common_types(limit=300)
				#print len( currentState.space.shapes )
				theDevMenu.menuState.deleteLastChar = True
			elif theDevMenu.menuState.keyboardEnabled:
				if 0 <= event.key < 256:
					if shiftHeld:
						someChr = chr( event.key ).upper()
						if someChr == ";":
							someChr = ":"
					else:
						someChr = chr( event.key )
					if someChr.isalnum() or someChr == ":":
						theDevMenu.menuState.keyboardInput( someChr )
			
		elif event.type == MOUSEBUTTONDOWN:
			curMousePos = event.pos[0] + currentState.panX, event.pos[1] + currentState.panY
			if event.button == 1 and theDevMenu.open:
				theDevMenu.clicks['mouse1down'].append( curMousePos )
			elif event.button == 2 and theDevMenu.open:
				theDevMenu.clicks['mouse2down'].append( curMousePos )
			elif event.button == 3 and theDevMenu.open:
				theDevMenu.clicks['mouse3down'].append( curMousePos )
		
		elif event.type == MOUSEBUTTONUP:
			theDevMenu.draggingMenu = False
			theDevMenu.draggedSpot = [0,0]
			curMousePos = event.pos[0] + currentState.panX, event.pos[1] + currentState.panY
			if event.button == 1 and theDevMenu.open:
				theDevMenu.clicks['mouse1up'].append( curMousePos )
			elif event.button == 2 and theDevMenu.open:
				theDevMenu.clicks['mouse2up'].append( curMousePos )
			elif event.button == 3 and theDevMenu.open:
				theDevMenu.clicks['mouse3up'].append( curMousePos )

	currentState.sendInput( inputDict )
	
	inputDict = {}
	
	pygame.display.update( updatedArea )
	#pygame.display.update( )

	updatedArea = []

	timeTillFpsPrint -= float(timer.get_time())/1000
	if timeTillFpsPrint < 0:
		print timer.get_fps()
		timeTillFpsPrint = 2.0
	timer.tick( 60 )
