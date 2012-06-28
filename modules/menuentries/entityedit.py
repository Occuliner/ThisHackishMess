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

"""This file defines the EntButton, EntityEditState, and EntityEditButton classes.\n
EntityEditButton is the button that appears in the default DevMenu state.\n
EntityEditState is the menu state invoked when EntityEditButton is pressed.\n
EnButton is a generic Button class that is inited from a given Entity-class\n
for use the EntityEditState."""
import pygame

from imageload import loadImage

from button import Button

from menustate import MenuState

from gridrounding import gridRound

from scale import scaleSurface

from staticimage import StaticImage

from selectionbox import SelectionBox

from label import Label

class EntButton( Button ):
	"""EntButton is a generic class that inits a Button from a given Entity-class.\n""" \
	"""It is used in EntityEditState to create buttons to pick which entity type to\n""" \
	"""place."""
	def __init__( self, entity, entNum, pos, parentState=None ):
		
		firstFrame = entity.sheet.subsurface( pygame.Rect( 0, 0, entity.width, entity.height ) )
		Button.__init__( self, scaleSurface( firstFrame, 0.5 ), pos, parentState )

		self.entNum = entNum

	def push( self, clickKey ):
		"""This method sets the parent state (which should always be EntityEditState)\n""" \
		""" to be using this Button's given entity in the Entity-placing functionality."""
		if clickKey is 'mouse1up':
			#print self.entNum
			if self.parentState.selectedButton is self:
				return None
			self.parentState.selectedButton = self
			self.parentState.entNum = self.entNum
			self.parentState.removeSprite( self.parentState.entSelectionBox )
			self.parentState.entSelectionBox = SelectionBox( self.rect, self.parentState )
			self.parentState.addSprite( self.parentState.entSelectionBox )
			self.parentState.menu.loadMenuState( self.parentState )
		
class EntityEditState( MenuState ):
	"""EntityEditState is a MenuState class that creates Entity-placing functionality,\n""" \
	"""to put dynamic objects into the game's playState.\n""" \
	"""It still needs Entity removal, Entity dragging and snap-to-grid functionality.\n"""
	def __init__( self, menu, sprites=[] ):
		MenuState.__init__( self, menu, sprites )

		self.entNum = 0
		self.sprites = [self.fileNameLabel]
		self.buttons = []

		self.panel = StaticImage(loadImage("devmenu.png"), (10, 10))
		self.addSprite( self.panel )
		
		self.curEntNum = 0
		self.xPos = 0
		self.yPos = 0
		self.tallest = 0
		self.processedEnts = []

		self.generateButtons()

		self.selectedButton = self.buttons[self.entNum]
		self.entSelectionBox = SelectionBox( self.selectedButton.rect, self )
		self.addSprite( self.entSelectionBox )

		#curEntNum = 0
		#xPos = 0
		#yPos = 0
		#tallest = 0
		#for eachEnt in self.menu.masterEntSet.getEnts():
		#	position = ( xPos + 21, yPos + 30 )
		#	self.addButton( EntButton( eachEnt, curEntNum, position, self ) )
		#	xPos += eachEnt.width
		#	tallest = max( tallest, eachEnt.height )
		#	if xPos > 108:
		#		xPos = 0
		#		yPos += tallest
		#	curEntNum += 1
		#
		self.curGrabbedEnt = None
		self.lastMouseSpot = ( 0, 0 )

	def generateButtons( self ):
		newEnts = self.menu.masterEntSet.getEnts()
		if len( newEnts ) == len( self.processedEnts ):
			return None
		for eachEnt in [ each for each in newEnts if each not in self.processedEnts ]:
		#for eachEnt in newEnts:
			position = ( self.xPos + 21, self.yPos + 30 )
			self.addButton( EntButton( eachEnt, self.curEntNum, position, self ) )
			self.processedEnts.append( eachEnt )
			self.xPos += eachEnt.width
			self.tallest = max( self.tallest, eachEnt.height )
			if self.xPos > 108:
				self.xPos = 0
				self.yPos += self.tallest
			self.curEntNum += 1
		self.menu.loadMenuState( self )

	def getPressedEnt( self, point ):
		"""See which ent is at this point"""
		escape = False
		for eachSpriteList in ( eachGroup.sprites() for eachGroup in self.menu.playState.groups ):
			for eachSprite in [ sprite for sprite in eachSpriteList if not sprite.notDirectlyRemovable]:
				if eachSprite.rect.collidepoint( point ):
					#self.curGrabbedEnt = eachSprite
					return eachSprite

	def update( self, dt, click, clickKey, curMousePos=None ):
		"""Generic update method. The actual Entity-placing happens in here."""
		#print len( self.menu.playState.sprites() )
		self.generateButtons()
		if click is not None:
			if clickKey is 'mouse1down':
				self.curGrabbedEnt = self.getPressedEnt( curMousePos )

			elif clickKey is 'mouse1up':
				if self.getPressedEnt( click ) == None and self.curGrabbedEnt == None:
					#print self.entNum
					#theClass = self.menu.masterEntSet.getEnts()[self.entNum]( list( click ), vel=[0,0], group=self.menu.playState.playersGroup )
					#HOLY DAMN HELL CONNOR MAKE IT GET THE CORRECT GROUP TO ADD TO, POSSIB. USE A DICTIONARY AND A STRING IN EACH CLASS DEF
				
					#classDef = self.menu.masterEntSet.getEnts()[self.entNum]
					classDef = self.processedEnts[self.entNum]
					destGroup = getattr( self.menu.playState, classDef.playStateGroup )
					classDef( list( click ), vel=[0,0], group=destGroup )
				self.curGrabbedEnt = None
			
			elif clickKey is 'mouse3up':
				anEnt = self.getPressedEnt( click )
				if anEnt is not None:
					anEnt.kill()

		elif curMousePos is not None:
			deltaPos = curMousePos[0] - self.lastMouseSpot[0], curMousePos[1] - self.lastMouseSpot[1]
			if self.curGrabbedEnt is not None:
				self.curGrabbedEnt.body.position[0] += deltaPos[0]
				self.curGrabbedEnt.body.position[1] += deltaPos[1]
			self.lastMouseSpot = curMousePos
				
				
		


class EntityEditButton( Button ):
	"""EntityEditButton is a Button that appears in the DefaultMenuState.\n"""\
	"""It merely invokes the EntityEditState MenuState."""
	image = loadImage("entityeditbutton.png")
	rect = image.get_rect()
	rect.topleft = ( 24, 44 )
	def __init__( self, menu=None ):
		Button.__init__( self, None, None, menu )

	def push( self, clickKey ):
		"""Invokes the EntityEditState MenuState on the parentState's DevMenu."""
		if "up" in clickKey:
			anEntityEditState = EntityEditState( self.parentState.menu )
			self.parentState.menu.loadMenuState( anEntityEditState )

