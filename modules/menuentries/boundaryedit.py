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

import pygame, os

from imageload import loadImage

from button import Button

from menustate import MenuState

from staticimage import StaticImage

from gridrounding import gridRound

from selectionbox import SelectionBox

from label import Label

class SnapToGridButton( Button ):
    image = loadImage("gridbutton.png", 2 )
    def __init__( self, menu=None ):
        Button.__init__( self, None, None, menu )
        self.rect = self.image.get_rect()
        self.rect.topleft = ( 84, 24 )
    def push( self, clickKey, click ):
        if "up" in clickKey:
            self.parentState.toggleSnapToGrid()

class RemoveBoundaryButton( Button ):
    image = loadImage("remove.png", 2 )
    def __init__( self, menu=None ):
        Button.__init__( self, None, None, menu )
        self.rect = self.image.get_rect()
        self.rect.topleft = ( 24, 24 )
    def push( self, clickKey, click ):
        if "up" in clickKey:
            self.parentState.removeMode()

class AddBoundaryButton( Button ):
    image = loadImage("add.png", 2 )
    def __init__( self, menu=None ):
        Button.__init__( self, None, None, menu )
        self.rect = self.image.get_rect()
        self.rect.topleft = ( 54, 24 )
    def push( self, clickKey, click ):
        if "up" in clickKey:
            self.parentState.addMode()

class BoundaryEditButton( Button ):
    image = loadImage("boundaryeditbutton.png", 2 )
    rect = image.get_rect()
    rect.topleft = ( 24, 124 )
    def __init__( self, menu=None ):
        Button.__init__( self, None, None, menu )

    def push( self, clickKey, click ):
        if "up" in clickKey:
            aBoundEditState = BoundaryEditState( self.parentState.menu )
            self.parentState.menu.loadMenuState( aBoundEditState )

def distance( point1, point2 ):
    return ( (point1[0]-point2[0])**2 + (point1[1]-point2[1])**2 )**0.5

class BoundaryEditState( MenuState ):
    def __init__( self, menu, sprites=[] ):
        MenuState.__init__( self, menu, sprites )
        self.sprites = [self.fileNameLabel]
        self.buttons = []

        self.panel = StaticImage(loadImage("devmenu.png", 2 ), (10, 10))
        self.addSprite( self.panel )

        self.addBoundButton = AddBoundaryButton( self )
        self.addButton( self.addBoundButton )

        self.removeBoundButton = RemoveBoundaryButton( self )
        self.addButton( self.removeBoundButton )

        self.snapToGridButton = SnapToGridButton( self )
        self.addButton( self.snapToGridButton )

        self.buttonSelectionBox = SelectionBox( self.addBoundButton.rect, self )
        self.addSprite( self.buttonSelectionBox )
        
        self.gridButtonSelectionBox = None

        self.addingMode = True
        self.removingMode = False

        self.curStart = None
        self.gridX = 20
        self.gridY = 20
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

    def addMode( self ):
        self.addingMode = True
        self.removingMode = False
        self.removeSprite( self.buttonSelectionBox )
        self.buttonSelectionBox = SelectionBox( self.addBoundButton.rect, self )
        self.addSprite( self.buttonSelectionBox )
        self.menu.loadMenuState( self )

    def removeMode( self ):
        self.removingMode = True
        self.addingMode = False
        self.removeSprite( self.buttonSelectionBox )
        self.buttonSelectionBox = SelectionBox( self.removeBoundButton.rect, self )
        self.addSprite( self.buttonSelectionBox )
        self.menu.loadMenuState( self )

    def selectSegmentEnd( self, point, threshold ):
        possib = {}        
        for eachSegment in self.menu.playState.boundaries:
            lengthToA = distance( point, ( eachSegment.a[0], eachSegment.a[1] ) )
            if lengthToA < threshold:
                possib[lengthToA] = ( eachSegment, 'a' )
            lengthToB = distance( point, ( eachSegment.b[0], eachSegment.b[1] ) )
            if lengthToB < threshold:
                possib[lengthToB] = ( eachSegment, 'b' )
        if len( possib ) == 0:
            return None
        return sorted( possib.items(), cmp=lambda x, y: cmp( x[0], y[0] ) )[-1][1]

    def selectSegment( self, point, threshold ):
        possib = {}
        for eachSegment in self.menu.playState.boundaries:
            a, b = eachSegment.a, eachSegment.b
            lengthToA = distance( point, ( a[0], a[1] ) )
            lengthToB = distance( point, ( b[0], b[1] ) )
            sLength = (a-b).get_length()
            if lengthToA < sLength*1.1 and lengthToB < sLength*1.1:
                alphaLength = distance( point, ( a[0], a[1] ) )
                betaLength = distance( point, ( b[0], b[1] ) )
                cLength = float( alphaLength**2 - betaLength**2 + sLength**2 )/(2*sLength)
                trueDistance = ( alphaLength**2 - cLength**2 )**0.5
                if trueDistance < threshold:
                    possib[trueDistance] = eachSegment
            else:
                if lengthToA < threshold:
                    possib[lengthToA] = eachSegment
                if lengthToB < threshold:
                    possib[lengthToB] = eachSegment
        if len( possib ) == 0:
            return None
        return sorted( possib.items(), cmp=lambda x, y: cmp( x[0], y[0] ) )[-1][1]
        
    def update( self, dt, click, clickKey, curMousePos=None ):
        if self.curStart is not None:
            if self.snapToGrid:
                curPoint = gridRound( curMousePos, self.gridX, self.gridY, trueRounding=True )
            else:
                curPoint = curMousePos
            self.menu.playState.lineVisualiser.devMenuLineGroups = [ [ self.curStart, curPoint ] ]
            self.menu.playState.lineVisualiser.flush = True
        self.menu.playState.lineVisualiser.renderLines = True
        self.menu.playState.lineVisualiser.renderPhysicsLines = True
        self.menu.playState.lineVisualiser.forceNoRender = True
        if click is not None:
            if clickKey is 'mouse1down' and self.curStart is None and self.addingMode:
                if self.snapToGrid:
                    self.curStart = gridRound( curMousePos, self.gridX, self.gridY, trueRounding=True )
                else:
                    self.curStart = curMousePos
            elif clickKey is 'mouse1up' and self.addingMode:
                if self.snapToGrid:
                    curPoint = gridRound( curMousePos, self.gridX, self.gridY, trueRounding=True )
                else:
                    curPoint = curMousePos
                self.menu.playState.addBoundary( self.curStart, curPoint )
                self.curStart = None
            elif clickKey is 'mouse1up' and self.removingMode:
                segment = self.selectSegment( curMousePos, 10 )
                if segment is not None:
                    self.menu.playState.removeBoundary( segment )
            elif clickKey is 'mouse3down' and self.curStart is None:
                segmentEndPair = self.selectSegmentEnd( curMousePos, 10 )
                if segmentEndPair is not None:
                    self.menu.playState.removeBoundary( segmentEndPair[0] )
                    if segmentEndPair[1] is 'a':
                        damnPoint = segmentEndPair[0].b
                    else:
                        damnPoint = segmentEndPair[0].a
                    self.curStart = damnPoint.x, damnPoint.y
            elif clickKey is 'mouse3up' and self.curStart is not None:
                if self.snapToGrid:
                    curPoint = gridRound( curMousePos, self.gridX, self.gridY, trueRounding=True )
                else:
                    curPoint = curMousePos
                self.menu.playState.addBoundary( self.curStart, curPoint )
                self.curStart = None
