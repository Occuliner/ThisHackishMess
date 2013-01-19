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
		if entity.bWidth is not None and not entity.forceUseRect:
			firstFrame = entity.sheet.subsurface( pygame.Rect( entity.bdx, entity.bdy, entity.bWidth, entity.bHeight ) )
		elif entity.wbWidth is not None and not entity.forceUseRect:
			firstFrame = entity.sheet.subsurface( pygame.Rect( entity.wbdx, entity.wbdy, entity.wbWidth, entity.wbHeight ) )
		else:
			firstFrame = entity.sheet.subsurface( pygame.Rect( 0, 0, entity.width, entity.height ) )
		Button.__init__( self, scaleSurface( firstFrame, 0.5 ), pos, parentState )

		self.entNum = entNum

	def push( self, clickKey, click ):
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
		
class ScrollBackButton( Button ):
	def __init__( self, parentState=None ):
		Button.__init__( self, loadImage( "backarrowsmall.png", 2 ), ( 24, 380 ), parentState )
	def push( self, clickKey, click ):
		if "up" in clickKey:
			if self.parentState.curPage > 0:
				self.parentState.repage( self.parentState.curPage - 1 )

class ScrollNextButton( Button ):
	def __init__( self, parentState=None ):
		Button.__init__( self, loadImage( "forwardarrowsmall.png", 2 ), ( 116, 380 ), parentState )
	def push( self, clickKey, click ):
		if "up" in clickKey:
			if self.parentState.curPage < max( self.parentState.pages.keys() ):
				self.parentState.repage( self.parentState.curPage + 1 )

class SnapToGridButtonEnt( Button ):
	image = loadImage( "gridbutton.png", 2 )
	def __init__( self, menu=None ):
		Button.__init__( self, None, None, menu )
		self.rect = self.image.get_rect()
		self.rect.topleft = ( 114, 338 )
	def push( self, clickKey, click ):
		if "up" in clickKey:
			self.parentState.toggleSnapToGrid()

class EntityEditState( MenuState ):
	"""EntityEditState is a MenuState class that creates Entity-placing functionality,\n""" \
	"""to put dynamic objects into the game's playState.\n""" \
	"""It still needs Entity removal, Entity dragging and snap-to-grid functionality.\n"""
	def __init__( self, menu, sprites=[] ):
		MenuState.__init__( self, menu, sprites )

		self.entNum = 0
		self.sprites = [self.fileNameLabel]
		self.buttons = []

		self.panel = StaticImage(loadImage("devmenu.png", 2), (10, 10))
		self.addSprite( self.panel )

		self.scrollNextButton = ScrollNextButton( self )
		self.addButton( self.scrollNextButton )

		self.scrollBackButton = ScrollBackButton( self )
		self.addButton( self.scrollBackButton )

		self.snapToGridButton = SnapToGridButtonEnt( self )
		self.addButton( self.snapToGridButton )
		
		self.curEntNum = 0
		self.xPos = 0
		self.yPos = 0
		self.tallest = 0
		self.processedEnts = []

		self.pages = {0:[]}
		self.curPage = 0
		self.maxPage = 0
		self.generateButtons()

		self.snapToGrid = False
		self.gridButtonSelectionBox = None

		self.selectedButton = self.buttons[self.entNum+3]
		self.entSelectionBox = SelectionBox( self.selectedButton.rect, self )
		self.addSprite( self.entSelectionBox )

		self.curGrabbedEnt = None
		self.lastMouseSpot = ( 0, 0 )
		self.whereEntWasGrabbed = None

	def toggleSnapToGrid( self ):
		self.snapToGrid = not self.snapToGrid
		if self.gridButtonSelectionBox is None:
			self.gridButtonSelectionBox = SelectionBox( self.snapToGridButton.rect, self )
			self.addSprite( self.gridButtonSelectionBox )
		else:
			self.removeSprite( self.gridButtonSelectionBox )
			self.gridButtonSelectionBox = None
		self.menu.loadMenuState( self )

	def generateButtons( self ):
		newEnts = self.menu.masterEntSet.getEnts()
		if len( newEnts ) == len( self.processedEnts ):
			return None
		for eachEnt in [ each for each in newEnts if each not in self.processedEnts ]:
			position = ( self.xPos + 21, self.yPos + 30 )
			givenButton = EntButton( eachEnt, self.curEntNum, position, self )
			self.processedEnts.append( eachEnt )
			if self.pages.has_key( self.maxPage ):
				self.pages[self.maxPage].append( givenButton )
			else:
				self.pages[self.maxPage] = [ givenButton ]
			if eachEnt.bWidth is not None and not eachEnt.forceUseRect:
				self.xPos += (( eachEnt.scale*eachEnt.bWidth )/2 + 10)
				self.tallest = max( self.tallest, eachEnt.bHeight*0.5*eachEnt.scale )
			elif eachEnt.wbWidth is not None and not eachEnt.forceUseRect:
				self.xPos += (( eachEnt.scale*eachEnt.wbWidth )/2 + 10)
				self.tallest = max( self.tallest, eachEnt.wbHeight*0.5*eachEnt.scale )
			else:
				self.xPos += (( eachEnt.scale*eachEnt.width)/2 + 10)
				self.tallest = max( self.tallest, eachEnt.height*0.5*eachEnt.scale )
			if self.xPos > 108:
				self.xPos = 0
				self.yPos += self.tallest
				self.tallest = 0
			if self.yPos > 318:
				self.yPos = 0
				self.maxPage += 1
			self.curEntNum += 1
		[ self.addButton( each ) for each in self.pages[self.curPage] if each not in self.buttons ] 
		self.menu.loadMenuState( self )

	def repage( self, newPageNum ):
		map( self.removeButton, self.pages[self.curPage] )
		self.curPage = newPageNum
		map( self.addButton, self.pages[self.curPage] )
		if self.entNum not in [ each.entNum for each in self.pages[self.curPage] ] and self.tileSelectionBox in self.sprites:
			self.removeSprite( self.tileSelectionBox )
		elif self.entNum in [ each.entNum for each in self.pages[self.curPage] ] and self.tileSelectionBox not in self.sprites:
			self.addSprite( self.tileSelectionBox )
		self.menu.loadMenuState( self )

	def getPressedEnt( self, point ):
		"""See which ent is at this point"""
		escape = False
		for eachSpriteList in ( eachGroup.sprites() for eachGroup in self.menu.playState.groups ):
			for eachSprite in [ sprite for sprite in eachSpriteList if not sprite.notDirectlyRemovable]:
				if eachSprite.bWidth is not None:
					start = eachSprite.rect.topleft
					givenRect = pygame.Rect( (start[0] + eachSprite.bdx, start[1] + eachSprite.bdy), (eachSprite.bWidth, eachSprite.bHeight) )
				else:
					givenRect = eachSprite.rect
				if givenRect.collidepoint( point ):
					return eachSprite

	def update( self, dt, click, clickKey, curMousePos=None ):
		"""Generic update method. The actual Entity-placing happens in here."""
		#print len( self.menu.playState.sprites() )
		self.generateButtons()
		if click is not None:
			if clickKey is 'mouse1down':
				self.curGrabbedEnt = self.getPressedEnt( curMousePos )
				if self.curGrabbedEnt is not None:
					entPos = self.curGrabbedEnt.getPosition()
					self.whereEntWasGrabbed = curMousePos[0] - entPos[0], curMousePos[1] - entPos[1]

			elif clickKey is 'mouse1up':
				if self.getPressedEnt( click ) == None and self.curGrabbedEnt == None:
					classDef = self.processedEnts[self.entNum]
					destGroup = getattr( self.menu.playState, classDef.playStateGroup )
					dest = click[0]-self.menu.playState.panX, click[1]-self.menu.playState.panY
					if self.snapToGrid:
						if classDef.wbWidth is not None:
							dest = gridRound( dest, classDef.wbWidth, classDef.wbHeight )
						elif classDef.bWidth is not None:
							dest = gridRound( dest, classDef.bWidth, classDef.bHeight )
						else:
							dest = gridRound( dest, classDef.width, classDef.height )
					classDef( dest, vel=[0,0], group=destGroup )
				self.curGrabbedEnt = None
				self.whereEntWasGrabbed = None
			
			elif clickKey is 'mouse3up':
				anEnt = self.getPressedEnt( click )
				if anEnt is not None:
					anEnt.kill()
				self.whereEntWasGrabbed = None

		elif curMousePos is not None:
			if self.curGrabbedEnt is not None:
				curEnt = self.curGrabbedEnt
				newPos = curMousePos[0]-self.whereEntWasGrabbed[0], curMousePos[1]-self.whereEntWasGrabbed[1]
				if self.snapToGrid:
					if curEnt.wbWidth is not None:
						newPos = gridRound( newPos, curEnt.wbWidth, curEnt.wbHeight )
					elif curEnt.bWidth is not None:
						newPos = gridRound( newPos, curEnt.bWidth, curEnt.bHeight )
					else:
						newPos = gridRound( newPos, curEnt.width, curEnt.height )
				curEnt.setPosition( newPos )
			self.lastMouseSpot = curMousePos
				
				
		


class EntityEditButton( Button ):
	"""EntityEditButton is a Button that appears in the DefaultMenuState.\n"""\
	"""It merely invokes the EntityEditState MenuState."""
	image = loadImage("entityeditbutton.png", 2)
	rect = image.get_rect()
	rect.topleft = ( 24, 44 )
	def __init__( self, menu=None ):
		Button.__init__( self, None, None, menu )

	def push( self, clickKey, click ):
		"""Invokes the EntityEditState MenuState on the parentState's DevMenu."""
		if "up" in clickKey:
			anEntityEditState = EntityEditState( self.parentState.menu )
			self.parentState.menu.loadMenuState( anEntityEditState )

