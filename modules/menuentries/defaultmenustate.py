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

"""This file defines the DefaultMenuState Class.\n""" \
"""It is a type of MenuState for the DevMenu, can you guess which one?"""

from menustate import MenuState

from flooredit import FloorEditButton

from entityedit import EntityEditButton

from loadmap import LoadMapButton

from savemap import SaveMapButton

from tagedit import TagEditButton

from boundaryedit import BoundaryEditButton

from sensoredit import SensorEditButton

from physicsvis import PhysicsVisButton

from staticimage import StaticImage

from imageload import loadImage

from label import Label

from networkbuttons import ConnectToButton, HostButton

from pausestart import PauseStartButton

from button import Button

import pygame, os

class LimitField( Button ):
    font = pygame.font.Font( os.path.join( "data", "fonts", "PD-tarzeau_-_Atari_Small.ttf" ), 16 )
    def __init__( self, parentState=None, prefix = "", text="", pos=(0,0) ):
        Button.__init__( self, None, None, parentState )
        self.prefix = prefix
        self.text = text
        self.rect = pygame.Rect( 0, 0, 0, 0 ).move( pos[0], pos[1] )
        self.selected = False
        self.createText()

    def setLimits( self, x1, x2, y1, y2 ):
        playState = self.parentState.menu.playState
        playState.limitX1, playState.limitX2, playState.limitY1,playState.limitY2 = x1, x2, y1, y2

    def renderImage( self ):
        if self.selected:
            self.background.fill( pygame.Color( 255, 0, 0 ) )
            self.image.blit( self.background, (0, 0) )
            self.image.blit( self.textImage, (0, 0) )
        else:
            self.image = self.textImage.copy().convert(32)
          
    def createText( self ):
        oldX, oldY = self.rect.topleft
        self.textImage = self.font.render( self.prefix+self.text, False, pygame.Color( 0, 0, 0 ) )
        damnRect = self.textImage.get_rect()
        self.background = pygame.Surface( ( damnRect.w, damnRect.h ), depth=32 )
        self.image = pygame.Surface( ( damnRect.w, damnRect.h ) )
        self.renderImage()
        self.rect = damnRect
        self.rect.topleft = oldX, oldY

    def toggleSelect( self ):
        self.selected = not self.selected
        self.renderImage()
        if not self.selected:
            try:
                val = int( self.text )
                foundVal = True
            except:
                if self.text == "":
                    val = None
                    foundVal = True
                else:
                    foundVal = False
            if self.prefix == "Left: " and foundVal:
                self.parentState.menu.playState.limitX1 = val
            if self.prefix == "Right: " and foundVal:
                self.parentState.menu.playState.limitX2 = val
            if self.prefix == "Top: " and foundVal:
                self.parentState.menu.playState.limitY1 = val
            if self.prefix == "Bottom: " and foundVal:
                self.parentState.menu.playState.limitY2 = val
        if self.parentState.field is not None:
            if self.parentState.field is not self and self.selected:
                self.parentState.field.toggleSelect()
                self.parentState.field = self
            if self.parentState.field is self and not self.selected:
                self.parentState.field = None
        else:
            if self.selected:
                self.parentState.field = self
            else:
                self.parentState.field = None

    def push( self, clickKey, click ):
        if "up" in clickKey:
            self.toggleSelect()

class DefaultMenuState( MenuState ):
    """The DefaultMenuState is the class for the default MenuState.\n""" \
    """Shocking, I know."""
    floorEditButton = FloorEditButton()

    entityEditButton = EntityEditButton()

    saveMapButton = SaveMapButton()

    loadMapButton = LoadMapButton()

    tagEditButton = TagEditButton()

    boundEditButton = BoundaryEditButton()

    physicsVisButton = PhysicsVisButton()

    sensorEditButton = SensorEditButton()

    connectToButton = ConnectToButton()

    hostButton = HostButton()

    pauseStartButton = PauseStartButton()

    panel = StaticImage( loadImage("devmenu.png", 2), (10, 10) )

    def __init__( self, menu, sprites=[panel, floorEditButton, entityEditButton, saveMapButton, loadMapButton, tagEditButton, boundEditButton, physicsVisButton, sensorEditButton, connectToButton, hostButton, pauseStartButton] ):
        MenuState.__init__( self, menu, sprites )
        self.limitLabel = Label( self, "Pan Limits:", ( 24, 204 ), 16, False )
        self.limitX1 = LimitField( self, prefix = "Left: ", text="", pos=( 24, 224 ) )
        self.limitX2 = LimitField( self, prefix = "Right: ", text="", pos=( 24, 240 ) )
        self.limitY1 = LimitField( self, prefix = "Top: ", text="", pos=( 24, 256 ) )
        self.limitY2 = LimitField( self, prefix = "Bottom: ", text="", pos=( 24, 272 ) )
        self.keyboardEnabled = True
        self.addSprite( self.limitLabel )
        self.addButton( self.limitX1 )
        self.addButton( self.limitX2 )
        self.addButton( self.limitY1 )
        self.addButton( self.limitY2 )
        self.field = None

    def update( self, dt, click, clickKey, curMousePos=None ):
        MenuState.update( self, dt, click, clickKey, curMousePos )
        inputText = self.getKeyboardInput()
        if self.field is not None:
            oldText = self.field.text
            if self.deleteLastChar:
                self.field.text =  self.field.text[:-1]
                self.deleteLastChar = False
            self.field.text += inputText
            if self.field.text != oldText:
                self.field.createText()
