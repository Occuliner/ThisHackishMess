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
        self.sprites = [self.fileNameLabel, self.miniMap]
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
        tmpGrdRect = self.menu.playState.floor.tileSet.getTiles()[0].image.get_rect()
        self.gridX, self.gridY = tmpGrdRect.w, tmpGrdRect.h
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
        MenuState.update( self, dt, click, clickKey, curMousePos )
        playState = self.menu.playState
        curMousePos = curMousePos[0]-playState.panX, curMousePos[1]-playState.panY
        if self.curStart is not None:
            if self.snapToGrid:
                curPoint = gridRound( curMousePos, self.gridX, self.gridY, trueRounding=True )
            else:
                curPoint = curMousePos
            playState.lineVisualiser.devMenuLineGroups = [ [ (self.curStart[0]+playState.panX, self.curStart[1]+playState.panY), (curPoint[0]+playState.panX, curPoint[1]+playState.panY) ] ]
            playState.lineVisualiser.flush = True
        playState.lineVisualiser.renderLines = True
        playState.lineVisualiser.renderPhysicsLines = True
        playState.lineVisualiser.forceNoRender = True
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
                playState.addBoundary( self.curStart, curPoint )
                self.curStart = None
            elif clickKey is 'mouse1up' and self.removingMode:
                segment = self.selectSegment( curMousePos, 10 )
                if segment is not None:
                    playState.removeBoundary( segment )
            elif clickKey is 'mouse3down' and self.curStart is None:
                segmentEndPair = self.selectSegmentEnd( curMousePos, 10 )
                if segmentEndPair is not None:
                    playState.removeBoundary( segmentEndPair[0] )
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
                playState.addBoundary( self.curStart, curPoint )
                self.curStart = None
