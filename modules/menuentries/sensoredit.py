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

import pygame, os

from modules.entitysets.puresensor import PureSensor

from imageload import loadImage

from button import Button

from menustate import MenuState

from staticimage import StaticImage

from gridrounding import gridRound

from selectionbox import SelectionBox

from label import Label

class SnapToGridButton( Button ):
    image = loadImage( "gridbutton.png", 2 )
    def __init__( self, menu=None ):
        Button.__init__( self, None, None, menu )
        self.rect = self.image.get_rect()
        self.rect.topleft = ( 24, 24 )
    def push( self, clickKey, click ):
        if "up" in clickKey:
            self.parentState.toggleSnapToGrid()

class SensorEditButton( Button ):
    image = loadImage( "sensoreditbutton.png", 2 )
    rect = image.get_rect()
    rect.topleft = ( 24, 144 )
    def __init__( self, menu=None ):
        Button.__init__( self, None, None, menu )

    def push( self, clickKey, click ):
        if "up" in clickKey:
            aBoundEditState = SensorEditState( self.parentState.menu )
            self.parentState.menu.loadMenuState( aBoundEditState )

class SensorEditState( MenuState ):
    def __init__( self, menu, sprites=[] ):
        MenuState.__init__( self, menu, sprites )
        self.sprites = [self.fileNameLabel, self.miniMap]
        self.buttons = []

        self.panel = StaticImage(loadImage( "devmenu.png", 2 ), (10, 10))
        self.addSprite( self.panel )

        self.snapToGridButton = SnapToGridButton( self )
        self.addButton( self.snapToGridButton )
        
        self.gridButtonSelectionBox = None

        self.addingMode = True
        self.removingMode = False

        self.curStart = None
        self.gridX = 32
        self.gridY = 32
        self.snapToGrid = False

    def toggleSnapToGrid( self ):
        self.snapToGrid = not self.snapToGrid
        if self.gridButtonSelectionBox is None:
            self.gridButtonSelectionBox = SelectionBox( self.snapToGridButton.rect, self )
            self.addSprite( self.gridButtonSelectionBox )
        else:
            self.removeSprite( self.gridButtonSelectionBox )
            self.gridButtonSelectionBox = None
        self.menu.loadMenuState( self )
        
    def getPressedSensor( self, point ):
        """See which sensor is at this point"""
        escape = False
        for eachSpriteList in ( eachGroup.sprites() for eachGroup in self.menu.playState.groups ):
            for eachSprite in [ sprite for sprite in eachSpriteList if sprite.pureSensor]:
                if eachSprite.rect.collidepoint( point ):
                    return eachSprite
    
    def update( self, dt, click, clickKey, curMousePos=None ):
        MenuState.update( self, dt, click, clickKey, curMousePos )
        if self.curStart is not None:
            if self.snapToGrid:
                curPoint = gridRound( curMousePos, self.gridX, self.gridY, trueRounding=True )
            else:
                curPoint = curMousePos
            self.menu.playState.lineVisualiser.devMenuLineGroups = [ [ self.curStart, ( self.curStart[0], curPoint[1] ) ],
                     [ ( self.curStart[0], curPoint[1] ), curPoint ], [ curPoint, ( curPoint[0], self.curStart[1] ) ], [ ( curPoint[0], self.curStart[1] ), self.curStart ] ]
            self.menu.playState.lineVisualiser.flush = True
        self.menu.playState.lineVisualiser.renderLines = True
        self.menu.playState.lineVisualiser.renderPhysicsLines = True
        self.menu.playState.lineVisualiser.forceNoRender = True
        if click is not None:
            if clickKey is 'mouse1down' and self.curStart is None:
                if self.snapToGrid:
                    self.curStart = gridRound( curMousePos, self.gridX, self.gridY, trueRounding=True )
                else:
                    self.curStart = curMousePos
            elif clickKey is 'mouse1up':
                if self.snapToGrid:
                    curPoint = gridRound( curMousePos, self.gridX, self.gridY, trueRounding=True )
                else:
                    curPoint = curMousePos
                #ADD SENSOR HERE
                destPoint = min( self.curStart[0], curPoint[0] ), min( self.curStart[1], curPoint[1] )
                w = abs( self.curStart[0] - curPoint[0] )
                h = abs( self.curStart[1] - curPoint[1] )
                destPoint = destPoint[0] + w/2, destPoint[1] + h/2
                destGroup = getattr( self.menu.playState, PureSensor.playStateGroup )
                PureSensor( pos=destPoint, group=destGroup, width=w, height=h )
                self.curStart = None
            elif clickKey is 'mouse3up':
                pickedSensor = self.getPressedSensor( curMousePos )
                if pickedSensor is not None:
                    pickedSensor.kill()
                #REMOVE SENSOR HERE
