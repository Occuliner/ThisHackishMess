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
	def push( self, clickKey ):
		if "up" in clickKey:
			self.parentState.menu.playState.swap( loadPlayState( os.path.join( "data", "maps", self.text ), self.parentState.menu.playState.floor.tileSet ) )
			self.parentState.menu.rerenderEverythingIn = 1
			self.parentState.menu.backToDefault()
		

class LoadMapButton( Button ):
	"""Load the current playState with cPickle."""
	image = loadImage( "loadmapbutton.png" )
	rect = image.get_rect()
	rect.topleft = ( 24, 84 )
	def __init__( self, parentState=None ):
		Button.__init__( self,  None, None, parentState )

	def push( self, clickKey ):
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
		
