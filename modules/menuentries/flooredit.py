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

from gridrounding import gridRound

class UndoButton( Button ):
    """UndoButton class, pretty obvious what it does."""
    image = loadImage("undo.png", 2)
    
    def __init__( self, parentState=None ):
        Button.__init__( self, None, None, parentState )
        self.rect = self.image.get_rect()
        self.rect.topleft = ( 44, 18 )
    def push( self, clickKey, click ):
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
    def push( self, clickKey, click ):
        if clickKey is 'mouse1up':
            self.parentState.floor.redoChange()

class HardBlitButton( Button ):
    image = loadImage( "hardblit.png", 2 )
    def __init__( self, menu=None ):
        Button.__init__( self, None, None, menu )
        self.rect = self.image.get_rect()
        self.rect.topleft = ( 73, 370 ) #( 144, 338 )
    def push( self, clickKey, click ):
        if "up" in clickKey:
            self.parentState.toggleHardBlit()

class SnapToGridButtonFloor( Button ):
    image = loadImage( "gridbutton.png", 2 )
    def __init__( self, menu=None ):
        Button.__init__( self, None, None, menu )
        self.rect = self.image.get_rect()
        self.rect.topleft = ( 114, 338 )
    def push( self, clickKey, click ):
        if "up" in clickKey:
            self.parentState.toggleSnapToGrid()

class RemoveFloorButton( Button ):
    image = loadImage("remove.png", 2 )
    def __init__( self, menu=None ):
        Button.__init__( self, None, None, menu )
        self.rect = self.image.get_rect()
        self.rect.topleft = ( 84, 338 )
    def push( self, clickKey, click ):
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
    def push( self, clickKey, click ):
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
    def push( self, clickKey, click ):
        if "up" in clickKey:
            self.parentState.applySelectionBox( self )
            self.parentState.editMode = 1
            self.parentState.setClampVisibility( False )

class TileButton( Button ):
    """TileButton class, is used for creating Buttons from a given tile in the FloorEditState."""
    def __init__( self, theTile, tileNum, pos, parentState=None ):
        Button.__init__( self, theTile.image, pos, parentState )
        self.tileNum = tileNum
    def push( self, clickKey, click ):
        """Sets the parentState (Should be FloorEditState) to start using this given Tile."""
        if clickKey is 'mouse1up':
            if (self.parentState.tileNum is not self.tileNum) or self.parentState.editMode is not 0:
                self.parentState.tileNum = self.tileNum
                self.parentState.applySelectionBox( self )
                self.parentState.editMode = 0
                self.parentState.setClampVisibility( False )

class ScrollBackButtonTiles( Button ):
    def __init__( self, parentState=None ):
        Button.__init__( self, loadImage( "backarrowsmall.png", 2 ), ( 24, 380 ), parentState )
    def push( self, clickKey, click ):
        if "up" in clickKey:
            if self.parentState.curPage > 0:
                self.parentState.repage( self.parentState.curPage - 1 )

class ScrollNextButtonTiles( Button ):
    def __init__( self, parentState=None ):
        Button.__init__( self, loadImage( "forwardarrowsmall.png", 2 ), ( 116, 380 ), parentState )
    def push( self, clickKey, click ):
        if "up" in clickKey:
            if self.parentState.curPage < max( self.parentState.pages.keys() ):
                self.parentState.repage( self.parentState.curPage + 1 )

class TopLeftLayerClamp( Button ):
    def __init__( self, parentState=None ):
        Button.__init__( self, loadImage( "topleftlayerclamp.png", 2 ), ( 0, 0 ), parentState )
    def push( self, clickKey, click ):
        if clickKey is "mouse1down":
            self.parentState.currentlyGrabbedClamp = 1
            self.parentState.grabPoint = ( click[0]-self.rect.x, click[1]-self.rect.y )
        if clickKey is "mouse1up":
            self.parentState.grabPoint = None
            self.parentState.currentlyGrabbedClamp = None
                
class BottomRightLayerClamp( Button ):
    def __init__( self, parentState=None ):
        Button.__init__( self, loadImage( "bottomrightlayerclamp.png", 2 ), ( 0, 0 ), parentState )
    def push( self, clickKey, click ):
        if clickKey is "mouse1down":
            self.parentState.currentlyGrabbedClamp = 2
            self.parentState.grabPoint = ( click[0]-self.rect.x, click[1]-self.rect.y )
        if clickKey is "mouse1up":
            self.parentState.grabPoint = None
            self.parentState.currentlyGrabbedClamp = None

class FloorEditState( MenuState ):
    """The FloorEditState class, a MenuState for editing the current PlayState's Floor."""
    #Create the floorEditUpdate function, and create a loop that generates a grid of all of the tiles to select from.
    #Each tile should be converted into a button, the button has the same image, and the push() method sets FloorEditState's current tileNum to it's tile.

    #TileGroups should be a class, and each group a metaclass, so that new tiles can be added while the program is running.
        
    def __init__( self, menu, sprites=[] ):
        MenuState.__init__( self, menu, sprites )

        self.buttons = []
        self.sprites = [self.fileNameLabel, self.miniMap]

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

        self.snapToGridButton = SnapToGridButtonFloor( self )
        self.addButton( self.snapToGridButton )

        self.hardBlitButton = HardBlitButton( self )
        self.addButton( self.hardBlitButton )
        
        #A local copy to prevent excessive look ups.
        self.floor = self.menu.playState.floor

        self.currentFloorLayer = 0

        self.currentLayerIsGrabbed = False
        self.grabPoint = None

        self.snapToGrid = False
        self.gridButtonSelectionBox = None

        self.hardBlit = False
        self.hardBlitSelectionBox = None

        self.currentlyGrabbedClamp = None

        #Edit modes are zero for tiles, 1 for creating/editing layers, 2 for select/edit, and 3 for removing
        self.editMode = 0

        self.tileNum = 0
        self.tileFillRect = None

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

        self.gridX, self.gridY = self.curSelectedButton.rect.w, self.curSelectedButton.rect.h
        self.setClamps()

    def applySelectionBox( self, button ):
        if self.tileSelectionBox in self.sprites:
                self.removeSprite( self.tileSelectionBox )
        self.tileSelectionBox = SelectionBox( button.rect, self )
        self.addSprite( self.tileSelectionBox )
        self.curSelectedButton = button
        self.menu.loadMenuState( self )

    def toggleSnapToGrid( self ):
        self.snapToGrid = not self.snapToGrid
        if self.gridButtonSelectionBox is None:
            self.gridButtonSelectionBox = SelectionBox( self.snapToGridButton.rect, self )
            self.addSprite( self.gridButtonSelectionBox )
        else:
            self.removeSprite( self.gridButtonSelectionBox )
            self.gridButtonSelectionBox = None
        self.menu.loadMenuState( self )

    def toggleHardBlit( self ):
        self.hardBlit = not self.hardBlit
        if self.hardBlitSelectionBox is None:
            self.hardBlitSelectionBox = SelectionBox( self.hardBlitButton.rect, self )
            self.addSprite( self.hardBlitSelectionBox )
        else:
            self.removeSprite( self.hardBlitSelectionBox )
            self.hardBlitSelectionBox = None
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
            self.addButton( self.topLeftLayerClamp, 0 )
            self.addButton( self.bottomRightLayerClamp, 0 )
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

    def makeTileRect( self, p1, p2 ):
        curTile = self.processedTiles[self.tileNum]
        height = curTile.rect.h
        width = curTile.rect.w
        floorRect = self.floor.layers[self.currentFloorLayer].rect
        leftBoundary = min( p2[0], p1[0] )-floorRect.left
        rightBoundary = max( p2[0], p1[0] )-floorRect.left
        topBoundary = min( p2[1], p1[1] )-floorRect.top
        bottomBoundary = max( p2[1], p1[1] )-floorRect.top
        x1Position, y1Position = gridRound( [ leftBoundary, topBoundary ], width, height, roundToTopLeft=True )
        x2Position, y2Position = gridRound( [ rightBoundary, bottomBoundary], width, height, roundToTopLeft=False )
        return pygame.Rect( x1Position, y1Position, x2Position-x1Position, y2Position-y1Position )
    
    def update( self, dt, click, clickKey, curMousePos=None ):
        """Where the actual Tile placing on the Floor happens."""
        self.menu.playState.lineVisualiser.devMenuLineGroups = []
        for eachLayer in self.floor.layers:
            self.menu.playState.lineVisualiser.devMenuLineGroups.extend( generateListOfLines( eachLayer.rect.topleft, eachLayer.rect.bottomright  ) )
        if self.startOfBlock is not None:
            if self.editMode is 0:
                self.tileFillRect = self.makeTileRect( self.startOfBlock, curMousePos )
                p1 = self.floor.layers[self.currentFloorLayer].rect.left+self.tileFillRect.left, self.floor.layers[self.currentFloorLayer].rect.top+self.tileFillRect.top
                p2 = p1[0]+self.tileFillRect.w, p1[1]+self.tileFillRect.h
                self.menu.playState.lineVisualiser.devMenuLineGroups.extend( generateListOfLines( p1, p2 ) )
                self.menu.playState.lineVisualiser.flush = True

            elif self.editMode is 1:
                if self.snapToGrid:
                    curPoint = gridRound( curMousePos, self.gridX, self.gridY, trueRounding=True )
                else:
                    curPoint = curMousePos
                self.menu.playState.lineVisualiser.devMenuLineGroups.extend( generateListOfLines( curPoint, self.startOfBlock ) )
                self.menu.playState.lineVisualiser.flush = True
        else:
            if self.editMode is 0:
                curTile = self.processedTiles[self.tileNum]
                floorRect = self.floor.layers[self.currentFloorLayer].rect
                displacedPoint = curMousePos[0]-floorRect.left, curMousePos[1]-floorRect.top
                p1 = gridRound( displacedPoint, self.gridX, self.gridY )
                p1 = p1[0]+floorRect.left, p1[1]+floorRect.top
                p2 = p1[0]+curTile.rect.w, p1[1]+curTile.rect.h
                self.menu.playState.lineVisualiser.devMenuLineGroups.extend( generateListOfLines( p1, p2 ) )
                self.menu.playState.lineVisualiser.flush = True
        self.menu.playState.lineVisualiser.renderLines = True
        self.menu.playState.lineVisualiser.forceNoRender = True
        if click is not None:
            if clickKey is 'mouse1down':
                if self.snapToGrid:
                    self.startOfBlock = gridRound( click, self.gridX, self.gridY, trueRounding=True )
                else:
                    self.startOfBlock = click
            elif clickKey is 'mouse1up':
                if self.editMode is 0:
                    if self.startOfBlock != None:
                        self.floor.writeArea( self.tileNum, self.tileFillRect, layerNum=self.currentFloorLayer, hardBlit=self.hardBlit )
                        self.startOfBlock = None
                        self.tileFillRect = None
                elif self.editMode is 1:
                    if self.startOfBlock != None:
                        if self.snapToGrid:
                            curPoint = gridRound( click, self.gridX, self.gridY, trueRounding=True )
                        else:
                            curPoint = click
                        newSize = ( abs( curPoint[0]-self.startOfBlock[0] ), abs( curPoint[1]-self.startOfBlock[1] ) )
                        newLayer = FloorLayer( newSize, ( min( curPoint[0], self.startOfBlock[0] ), min( curPoint[1], self.startOfBlock[1] ) ) )
                        self.floor.layers.append( newLayer )
                    self.grabPoint = None
                    self.currentlyGrabbedClamp = None
                elif self.editMode is 2:
                    if self.currentlyGrabbedClamp is None:
                        self.selectFloorLayer( click )
                    self.currentLayerIsGrabbed = False
                elif self.editMode is 3:
                    self.deleteFloorLayer( click )
                self.startOfBlock = None
                self.grabPoint = None
                self.currentlyGrabbedClamp = None
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
                if self.snapToGrid:
                    curPoint = gridRound( (curMousePos[0]-self.grabPoint[0], curMousePos[1]-self.grabPoint[1]), self.gridX, self.gridY, trueRounding=True )
                else:
                    curPoint = (curMousePos[0]-self.grabPoint[0], curMousePos[1]-self.grabPoint[1])
                self.floor.layers[self.currentFloorLayer].rect.topleft = curPoint
                self.setClamps()
            elif self.currentlyGrabbedClamp == 1:
                if self.snapToGrid:
                    curPoint = gridRound( curMousePos, self.gridX, self.gridY, trueRounding=True )
                else:
                    curPoint = curMousePos
                nx = curPoint[0]-self.grabPoint[0]
                ny = curPoint[1]-self.grabPoint[1]
                self.floor.layers[self.currentFloorLayer].resize( nx-self.topLeftLayerClamp.rect.left, 0, ny-self.topLeftLayerClamp.rect.top, 0 )
                self.setClamps()
            elif self.currentlyGrabbedClamp == 2:
                if self.snapToGrid:
                    curPoint = gridRound( curMousePos, self.gridX, self.gridY, trueRounding=True )
                else:
                    curPoint = curMousePos
                nx = curPoint[0]-self.grabPoint[0]
                ny = curPoint[1]-self.grabPoint[1]
                self.floor.layers[self.currentFloorLayer].resize( 0, nx-self.bottomRightLayerClamp.rect.left, 0, ny-self.bottomRightLayerClamp.rect.top )
                self.setClamps()

class FloorEditButton( Button ):
    """The FloorEditButton class, just creates a Button that invokes FloorEditState on the DevMenu."""
    image = loadImage("flooreditbutton.png", 2 )
    rect = image.get_rect()
    rect.topleft = ( 24, 24 )
    def __init__( self, parentState=None ):
        Button.__init__( self,  None, None, parentState )

    def push( self, clickKey, click ):
        """Invoke the FloorEditState"""
        #SWITCH TO FLOOREDIT MENU STATE
        if "up" in clickKey:
            aFloorEditState = FloorEditState( self.parentState.menu )
            self.parentState.menu.loadMenuState( aFloorEditState )
