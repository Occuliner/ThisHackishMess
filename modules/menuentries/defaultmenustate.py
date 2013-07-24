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
            if self.prefix == "Left: " and self.text.isdigit():
                self.parentState.menu.playState.limitX1 = int( self.text )
            if self.prefix == "Right: " and self.text.isdigit():
                self.parentState.menu.playState.limitX2 = int( self.text )
            if self.prefix == "Top: " and self.text.isdigit():
                self.parentState.menu.playState.limitY1 = int( self.text )
            if self.prefix == "Bottom: " and self.text.isdigit():
                self.parentState.menu.playState.limitY2 = int( self.text )
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
        self.limitLabel = Label( self, "World Limits:", ( 24, 204 ), 16 )
        self.limitX1 = LimitField( self, prefix = "Left: ", text="", pos=( 24, 224 ) )
        self.limitX2 = LimitField( self, prefix = "Right: ", text="", pos=( 24, 240 ) )
        self.limitY1 = LimitField( self, prefix = "Top: ", text="", pos=( 24, 256 ) )
        self.limitY2 = LimitField( self, prefix = "Bottom: ", text="", pos=( 24, 272 ) )
        self.addSprite( self.limitLabel )
        self.addButton( self.limitX1 )
        self.addButton( self.limitX2 )
        self.addButton( self.limitY1 )
        self.addButton( self.limitY2 )
        self.field = None

    def update( self, dt, click, clickKey, curMousePos=None ):
        MenuState.update( self, dt, click, clickKey, curMousePos )
        if self.field is not None:
            oldText = self.field.text
            if self.deleteLastChar:
                self.field.text =  self.field.text[:-1]
                self.deleteLastChar = False
            inputText = self.getKeyboardInput()
            print inputText
            self.field.text += inputText
            if self.field.text != oldText:
                self.field.createText()
