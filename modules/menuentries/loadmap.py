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
from picklestuff import loadPlayState
from filedialog import FileDialogState
import pygame
import os

class FileLoadButton( Button ):
    FileLoadButtonText = pygame.font.Font( os.path.join( "data", "fonts", "PD-tarzeau_-_Atari_Small.ttf" ), 24 )
    def __init__( self, parentState=None, text="", pos=(0,0) ):
        Button.__init__( self, None, None, parentState )
        self.text = text
        self.image = self.FileLoadButtonText.render( text, False, pygame.Color( 0, 0, 0 ) )
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
    def push( self, clickKey, click ):
        if "up" in clickKey:
            self.parentState.menu.playState.swap( loadPlayState( os.path.join( "data", "maps", self.text ), self.parentState.menu.playState.floor.tileSet, self.parentState.menu.masterEntSet.getEnts() ) )
            self.parentState.menu.rerenderEverythingIn = 1
            self.parentState.menu.backToDefault()
        

class LoadMapButton( Button ):
    """Load the current playState with cPickle."""
    image = loadImage( "loadmapbutton.png", 2 )
    rect = image.get_rect()
    rect.topleft = ( 24, 84 )
    def __init__( self, parentState=None ):
        Button.__init__( self,  None, None, parentState )

    def push( self, clickKey, click ):
        """Pull the state from a file"""
        #SWITCH TO FLOOREDIT MENU STATE
        if "up" in clickKey:
            aLoadMapState = LoadMapState( self.parentState.menu )
            self.parentState.menu.loadMenuState( aLoadMapState )

class LoadMapState( FileDialogState ):
    """The file browser for Loading."""
    def __init__( self, menu, sprites=[] ):
        sprites = []
        buttons = []
        FileDialogState.__init__( self, menu, FileLoadButton, sprites )
            
    def update( self, dt, click, clickKey, curMousePos=None ):
        oldString = self.currentString
        FileDialogState.update( self, dt, click, clickKey, curMousePos )
        if oldString != self.currentString:
            curText = self.userFont.render( self.currentString, False, pygame.Color( 0, 0, 0 ) )
            self.addSprite( StaticImage( curText, ( 40, 30 ) ) )
            self.menu.loadMenuState( self )
        
