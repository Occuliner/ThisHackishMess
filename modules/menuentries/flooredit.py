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

"""This file defines the FloorEditState, FloorEditButton and TileButton classes."""
import pygame

from imageload import loadImage

from button import Button

from menustate import MenuState

from gridrounding import gridRound

from staticimage import StaticImage

from selectionbox import SelectionBox

from label import Label

from floor import FloorLayer

from linegenfromcorners import generateListOfLines

class UndoButton( Button ):
	"""UndoButton class, pretty obvious what it does."""
	image = loadImage("undo.png", 2)
	
	def __init__( self, parentState=None ):
		Button.__init__( self, None, None, parentState )
		self.rect = self.image.get_rect()
		self.rect.topleft = ( 44, 18 )
	def push( self, clickKey ):
		"""Call Floor.undoChange() on the playState's floor."""
		if "up" in clickKey:
			self.parentState.floor.undoChange()

class RedoButton( Button ):
	"""RedoButton class, also pretty obvious what it does."""
	image = loadImage("redo.png", 2)
	
	def __init__( self, parentState=None ):
		Button.__init__( self, None, None, parentState )
		self.rect = self.image.get_rect()
		self.rect.topleft = ( 93, 18 )
	def push( self, clickKey ):
		if clickKey is 'mouse1up':
			self.parentState.floor.redoChange()

class RemoveFloorButton( Button ):
	image = loadImage("remove.png", 2 )
	def __init__( self, menu=None ):
		Button.__init__( self, None, None, menu )
		self.rect = self.image.get_rect()
		self.rect.topleft = ( 84, 338 )
	def push( self, clickKey ):
		if "up" in clickKey:
			self.parentState.applySelectionBox( self )
			self.parentState.editMode = 3
			self.parentState.setClampVisibility( False )

class EditFloorButton( Button ):
	image = loadImage("arrowedit.png", 2 )
	def __init__( self, menu=None ):
		Button.__init__( self, None, None, menu )
		self.rect = self.image.get_rect()
		self.rect.topleft = ( 54, 338 )
	def push( self, clickKey ):
		if "up" in clickKey:
			self.parentState.applySelectionBox( self )
			self.parentState.editMode = 2
			self.parentState.setClampVisibility( True )

class AddFloorButton( Button ):
	image = loadImage("add.png", 2 )
	def __init__( self, menu=None ):
		Button.__init__( self, None, None, menu )
		self.rect = self.image.get_rect()
		self.rect.topleft = ( 24, 338 )
	def push( self, clickKey ):
		if "up" in clickKey:
			self.parentState.applySelectionBox( self )
			self.parentState.editMode = 1
			self.parentState.setClampVisibility( False )

class TileButton( Button ):
	"""TileButton class, is used for creating Buttons from a given tile in the FloorEditState."""
	def __init__( self, theTile, tileNum, pos, parentState=None ):
		Button.__init__( self, theTile.image, pos, parentState )
		self.tileNum = tileNum
	def push( self, clickKey ):
		"""Sets the parentState (Should be FloorEditState) to start using this given Tile."""
		if clickKey is 'mouse1up' and self.parentState.tileNum is not self.tileNum:
			self.parentState.tileNum = self.tileNum
			self.parentState.applySelectionBox( self )
			self.parentState.editMode = 0

class ScrollBackButtonTiles( Button ):
	def __init__( self, parentState=None ):
		Button.__init__( self, loadImage( "backarrowsmall.png", 2 ), ( 24, 380 ), parentState )
	def push( self, clickKey ):
		if "up" in clickKey:
			if self.parentState.curPage > 0:
				self.parentState.repage( self.parentState.curPage - 1 )

class ScrollNextButtonTiles( Button ):
	def __init__( self, parentState=None ):
		Button.__init__( self, loadImage( "forwardarrowsmall.png", 2 ), ( 116, 380 ), parentState )
	def push( self, clickKey ):
		if "up" in clickKey:
			if self.parentState.curPage < max( self.parentState.pages.keys() ):
				self.parentState.repage( self.parentState.curPage + 1 )

class TopLeftLayerClamp( Button ):
	def __init__( self, parentState=None ):
		Button.__init__( self, loadImage( "topleftlayerclamp.png", 2 ), ( 0, 0 ), parentState )
	def push( self, clickKey ):
		if "down" in clickKey:
			pass
		elif "up" in clickKey:
			pass
				
class BottomRightLayerClamp( Button ):
	def __init__( self, parentState=None ):
		Button.__init__( self, loadImage( "bottomrightlayerclamp.png", 2 ), ( 0, 0 ), parentState )
	def push( self, clickKey ):
		if "down" in clickKey:
			pass
		elif "up" in clickKey:
			pass				

class FloorEditState( MenuState ):
	"""The FloorEditState class, a MenuState for editing the current PlayState's Floor."""
	#Create the floorEditUpdate function, and create a loop that generates a grid of all of the tiles to select from.
	#Each tile should be converted into a button, the button has the same image, and the push() method sets FloorEditState's current tileNum to it's tile.

	#TileGroups should be a class, and each group a metaclass, so that new tiles can be added while the program is running.
		
	def __init__( self, menu, sprites=[] ):
		MenuState.__init__( self, menu, sprites )

		#print len( self.buttons ), len( self.sprites ), len( sprites )
		self.buttons = []
		self.sprites = [self.fileNameLabel]

		self.panel = StaticImage( loadImage( "devmenu.png", 2 ), ( 10, 10 ) )
		self.addSprite( self.panel )

		self.undoButton = UndoButton( self )
		self.addButton( self.undoButton )

		self.redoButton = RedoButton( self )
		self.addButton( self.redoButton )

		self.scrollNextButton = ScrollNextButtonTiles( self )
		self.addButton( self.scrollNextButton )

		self.scrollBackButton = ScrollBackButtonTiles( self )
		self.addButton( self.scrollBackButton )

		self.removeFloorButton = RemoveFloorButton( self )
		self.addButton( self.removeFloorButton )

		self.addFloorButton = AddFloorButton( self )
		self.addButton( self.addFloorButton )

		self.editFloorButton = EditFloorButton( self )
		self.addButton( self.editFloorButton )

		self.topLeftLayerClamp = TopLeftLayerClamp( self )
		self.bottomRightLayerClamp = BottomRightLayerClamp( self )
		
		#A local copy to prevent excessive look ups.
		self.floor = self.menu.playState.floor

		self.currentFloorLayer = 0

		self.currentLayerIsGrabbed = False
		self.grabPoint = None

		#Edit modes are zero for tiles, 1 for creating/editing layers, 2 for select/edit, and 3 for removing
		self.editMode = 0

		self.tileNum = 0

		self.xPos = 0
		self.yPos = 0
		self.tallest = 0
		self.pages = {0:[]}
		self.curPage = 0
		self.processedTiles = []
		self.generateButtons()

		#For the tile placing functionality.
		self.startOfBlock = None

		self.tileSelectionBox = SelectionBox( self.pages[self.curPage][0].rect, self )
		self.addSprite( self.tileSelectionBox )
		self.curSelectedButton = self.pages[self.curPage][0]

	def applySelectionBox( self, button ):
		if self.tileSelectionBox in self.sprites:
				self.removeSprite( self.tileSelectionBox )
		self.tileSelectionBox = SelectionBox( button.rect, self )
		self.addSprite( self.tileSelectionBox )
		self.curSelectedButton = button
		self.menu.loadMenuState( self )

	def generateButtons( self ):
		curPageKey = max( self.pages.keys() )
		curTileNum = 0
		for eachTile in self.floor.tileSet.getTiles():
			position = ( self.xPos + 21, self.yPos + 50 )
			givenButton = TileButton( eachTile, curTileNum, position, self )
			if eachTile not in self.processedTiles:
				self.processedTiles.append( eachTile )
			#self.addButton( givenButton )
			if self.pages.has_key( curPageKey ):
				self.pages[curPageKey].append( givenButton )
			else:
				self.pages[curPageKey] = [ givenButton ]
			self.xPos += ( givenButton.rect.w )
			self.tallest = max( self.tallest, givenButton.rect.h )
			if self.xPos > 108:
				self.xPos = 0
				self.yPos += self.tallest
			if self.yPos > 278:
				self.yPos = 0
				curPageKey += 1
			curTileNum += 1
		map( self.addButton, self.pages[self.curPage] )

	def selectFloorLayer( self, click ):
		for eachNum, eachLayer in [each for each in enumerate( self.floor.layers )][::-1]:
			if eachLayer.rect.collidepoint( click ):
				if self.currentFloorLayer != eachNum:
					self.currentFloorLayer = eachNum
					break
		self.setClamps()

	def setClamps( self ):
		tlp = self.floor.layers[self.currentFloorLayer].rect.topleft
		brp = self.floor.layers[self.currentFloorLayer].rect.bottomright
		self.topLeftLayerClamp.rect.topleft = tlp[0]-15, tlp[1]-15
		self.bottomRightLayerClamp.rect.topleft = brp[0]-15, brp[1]-15

	def setClampVisibility( self, val ):
		if val and self.topLeftLayerClamp not in self.sprites:
			self.addButton( self.topLeftLayerClamp )
			self.addButton( self.bottomRightLayerClamp )
			self.menu.loadMenuState( self )
		elif not val and self.topLeftLayerClamp in self.sprites:
			self.removeButton( self.topLeftLayerClamp )
			self.removeButton( self.bottomRightLayerClamp )
			self.menu.loadMenuState( self )

	def deleteFloorLayer( self, click ):
		theNum = None
		for eachNum, eachLayer in [each for each in enumerate( self.floor.layers )][::-1]:
			if eachLayer.rect.collidepoint( click ):
				theNum = eachNum
				break
		if theNum is not None:
			self.floor.layers.pop( theNum )

	def repage( self, newPageNum ):
		map( self.removeButton, self.pages[self.curPage] )
		self.curPage = newPageNum
		map( self.addButton, self.pages[self.curPage] )
		if self.curSelectedButton in [self.addFloorButton, self.removeFloorButton]:
			pass
		else:
			if self.curSelectedButton not in self.pages[self.curPage]:
				if self.tileSelectionBox in self.sprites:
					self.removeSprite( self.tileSelectionBox )
			elif self.tileSelectionBox not in self.sprites:
				self.addSprite( self.tileSelectionBox )
		self.menu.loadMenuState( self )
	
	def update( self, dt, click, clickKey, curMousePos=None ):
		"""Where the actual Tile placing on the Floor happens."""
		self.menu.playState.lineVisualiser.devMenuLineGroups = []
		for eachLayer in self.floor.layers:
			self.menu.playState.lineVisualiser.devMenuLineGroups.extend( generateListOfLines( eachLayer.rect.topleft, eachLayer.rect.bottomright  ) )
		if self.startOfBlock is not None and click is not None:
			if self.editMode is 1:
				self.menu.playState.lineVisualiser.devMenuLineGroups.extend( generateListOfLines( click, self.startOfBlock ) )
				self.menu.playState.lineVisualiser.flush = True
		self.menu.playState.lineVisualiser.renderLines = True
		self.menu.playState.lineVisualiser.forceNoRender = True
		if click is not None:
			if clickKey is 'mouse1down':
				self.startOfBlock = click
			elif clickKey is 'mouse1up':
				if self.editMode is 0:
					if self.startOfBlock != None:
						curTile = self.processedTiles[self.tileNum]
					
						height = curTile.rect.h
						width = curTile.rect.w
					
						leftBoundary = min( click[0], self.startOfBlock[0] )-self.floor.layers[self.currentFloorLayer].rect.left
						rightBoundary = max( click[0], self.startOfBlock[0] )-self.floor.layers[self.currentFloorLayer].rect.left
						topBoundary = min( click[1], self.startOfBlock[1] )-self.floor.layers[self.currentFloorLayer].rect.top
						bottomBoundary = max( click[1], self.startOfBlock[1] )-self.floor.layers[self.currentFloorLayer].rect.top
	
						x1Position, y1Position = gridRound( [ leftBoundary, topBoundary ], width, height, roundToTopLeft=True )
						x2Position, y2Position = gridRound( [ rightBoundary, bottomBoundary], width, height, roundToTopLeft=False )
					
						self.floor.writeArea( self.tileNum, pygame.Rect( x1Position, y1Position, x2Position-x1Position, y2Position-y1Position ), layerNum=self.currentFloorLayer )
						self.startOfBlock = None
				elif self.editMode is 1:
					if self.startOfBlock != None:
						newSize = ( abs( click[0]-self.startOfBlock[0] ), abs( click[1]-self.startOfBlock[1] ) )
						newLayer = FloorLayer( newSize, ( min( click[0], self.startOfBlock[0] ), min( click[1], self.startOfBlock[1] ) ) )
						self.floor.layers.append( newLayer )
				elif self.editMode is 2:
					self.selectFloorLayer( click )
					self.currentLayerIsGrabbed = False
				elif self.editMode is 3:
					self.deleteFloorLayer( click )
			elif clickKey is 'mouse3down':
				if self.editMode is 2:
					self.currentLayerIsGrabbed = True
					self.grabPoint = ( click[0]-self.floor.layers[self.currentFloorLayer].rect.x, click[1]-self.floor.layers[self.currentFloorLayer].rect.y )
			elif clickKey is 'mouse3up':
				if self.editMode is 2:
					self.currentLayerIsGrabbed = False
					self.grabPoint = None
		elif curMousePos is not None:
			if self.currentLayerIsGrabbed and self.grabPoint is not None:
				self.floor.layers[self.currentFloorLayer].rect.topleft = (curMousePos[0]-self.grabPoint[0], curMousePos[1]-self.grabPoint[1])
				self.setClamps()

class FloorEditButton( Button ):
	"""The FloorEditButton class, just creates a Button that invokes FloorEditState on the DevMenu."""
	image = loadImage("flooreditbutton.png", 2 )
	rect = image.get_rect()
	rect.topleft = ( 24, 24 )
	def __init__( self, parentState=None ):
		Button.__init__( self,  None, None, parentState )

	def push( self, clickKey ):
		"""Invoke the FloorEditState"""
		#SWITCH TO FLOOREDIT MENU STATE
		if "up" in clickKey:
			aFloorEditState = FloorEditState( self.parentState.menu )
			self.parentState.menu.loadMenuState( aFloorEditState )
