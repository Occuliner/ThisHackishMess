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

from button import Button
from imageload import loadImage
from menustate import MenuState
from staticimage import StaticImage
from label import Label
import pygame
import os

class ScrollBackButtonFiles( Button ):
    def __init__( self, parentState=None ):
        Button.__init__( self, loadImage( "backarrow.png", 2 ), ( 42, 526 ), parentState )
    def push( self, clickKey, click ):
        if "up" in clickKey:
            if self.parentState.startButtonIndex - self.parentState.pageLength >= 0 and self.parentState.pageLength != 0:
                self.parentState.forceUpdate = True
                self.parentState.startButtonIndex -= self.parentState.pageLength

class ScrollNextButtonFiles( Button ):
    def __init__( self, parentState=None ):
        Button.__init__( self, loadImage( "forwardarrow.png", 2 ), ( 670, 526 ), parentState )
    def push( self, clickKey, click ):
        if "up" in clickKey:
            if self.parentState.startButtonIndex + self.parentState.pageLength < len( self.parentState.allTheFiles ) - 1:
                self.parentState.forceUpdate = True
                self.parentState.startButtonIndex += self.parentState.pageLength

class FileDialogState( MenuState ):
    """A file browser."""
    def __init__( self, menu, buttonType, sprites=[] ):
        self.panelImage = loadImage( "filebrowserbackground.png", 2 )
        self.panel = StaticImage( self.panelImage, ( 10, 10 ) )
        sprites.append( self.panel )
        self.backButton = ScrollBackButtonFiles( self )
        sprites.append( self.backButton )
        self.nextButton = ScrollNextButtonFiles( self )
        sprites.append( self.nextButton )
        MenuState.__init__( self, menu, sprites, miniMap = False )
        self.keyboardEnabled = True
        self.currentString = ""
        self.forceUpdate = False
        self.deleteLastChar = False
        self.oldString = ""
        self.boundingArea = pygame.Rect( 26, 26, 670, 496 )
        #self.addButton( FileButton( self, self.currentString, ( 40, 30 ) ) )
        
        self.startButtonIndex = 0
        self.pageLength = 0
        self.fileButtons = []
        
        self.buttonType = buttonType
        self.generateFileButtons()

        self.userFont = pygame.font.Font( os.path.join( "data", "fonts", "PD-tarzeau_-_Atari_Small.ttf" ), 24 )
        #Carry these sprites over each update.
        self.carryMeOverSprites = [ self.fileNameLabel ]
        self.carryMeOverButtons = []

        
    
    def generateFileButtons( self ):
        self.allTheFiles = self.generateListOfFiles( self.currentString )
        curX = 41
        curY = 71
        prevColumnLastIndex = -1
        self.fileButtons = []
        for num in xrange( self.startButtonIndex, len( self.allTheFiles ) ):
            eachFile = self.allTheFiles[num]
            eachButton = self.buttonType( self, eachFile, ( curX, curY ) )
            self.fileButtons.append( eachButton )
            if curY + eachButton.rect.h > self.boundingArea.bottom:
                curY = 71
                curX += max( [ each.rect.w for each in self.fileButtons[prevColumnLastIndex+1:num] ] ) + 8
                eachButton.rect.x, eachButton.rect.y = curX, curY
                prevColumnLastIndex = num  - self.startButtonIndex - 1
            if curX > self.boundingArea.right - 100:
                break
            self.addButton( eachButton )
            curY += eachButton.rect.h
        if len(self.fileButtons) > 0:
            self.pageLength = self.boundingArea.h/self.fileButtons[0].rect.h
        else:
            self.pageLengeth = 0

    def generateListOfFiles( self, givenString ):
        if givenString == "":
            return sorted( [ eachPath for eachPath in os.listdir( os.path.join( "data", "maps" ) ) if not os.path.isdir( eachPath ) ] )
        else:
            return sorted( [ eachPath for eachPath in os.listdir( os.path.join( "data", "maps" ) ) if not os.path.isdir( eachPath ) and givenString == eachPath[:len(givenString)] ] )
        
    def update( self, dt, click, clickKey, curMousePos=None ):
        #This font is for rendering what the user has input.
        if self.deleteLastChar:
            self.currentString = self.currentString[:-1]
            self.deleteLastChar = False
        self.currentString += self.getKeyboardInput()
        if self.currentString != self.oldString :
            self.forceUpdate = True
            self.startButtonIndex = 0
            self.pageLength = 0
        if self.forceUpdate:
            self.sprites, self.buttons = [ self.panel, self.backButton, self.nextButton ] + self.carryMeOverSprites, [ self.backButton, self.nextButton ] + self.carryMeOverButtons
            self.carryMeOverSprites, self.carryMeOverButtons = [], []
            #print self.currentString
            #curText = self.userFont.render( self.currentString, False, pygame.Color( 0, 0, 0 ) )
            #self.addSprite( StaticImage( curText, ( 40, 30 ) ) )
            self.generateFileButtons()
    
            self.menu.loadMenuState( self )
            self.oldString = self.currentString
            self.forceUpdate = False
            #This font is for rendering what is in the directory.
            #listFont = pygame.font.Font( fontName, fontSize )
            #listOfStuff = self.generateListOfFiles( self.givenString )
            #pass
