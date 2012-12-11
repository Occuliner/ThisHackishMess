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

"""This file defines the FloorChange and Floor classes."""
import pygame
from pygame.locals import SRCALPHA


#
#	Floor Class:
#	
#	Floor class is merely a class type that holds a list of tiles that will be used in that floor, and a floor surface.
#
#	The purpose of this is that you can write tile.images to the Floor.image at certain locations. And the Floor.image is rendered by the PlayState under the
#	in game entities.
#

#Also stored here, the FloorChange class, since giving it its own files seemed silly.

class FloorChange:
	"""The FloorChange class, this is merely an object to keep track of area changes.\n""" \
	"""It is created with a given position, and image.\n""" \
	"""Each of those attributes specifies what USED to be true of that given spot.\n""" \
	"""This is for use in undo/redo."""
	def __init__( self, image, pos, layerNum=0 ):
		#What the Floor used to look like at that spot.
		self.image = image
		self.pos = pos
		self.layerNum = layerNum

class FloorLayer( pygame.sprite.DirtySprite ):
	def __init__( self, size=None, pos=(0,0), image=None ):
		pygame.sprite.DirtySprite.__init__( self )
		if not (image is None):
			self.image = image
		else:
			self.image = pygame.Surface( size, SRCALPHA )
		self.rect = self.image.get_rect()
		self.rect.topleft = pos
	def resize( self, dleft, dright, dtop, dbottom ):
		tmpImage = self.image
		nx = self.rect.x + dleft
		ny = self.rect.y + dtop
		nsize = ( self.rect.w-dleft+dright, self.rect.h-dtop+dbottom )
		if nsize[0] < 1 or nsize[1] < 1:
			return None
		self.image = pygame.Surface( nsize, SRCALPHA )
		self.image.blit( tmpImage, ( -dleft, -dtop ) )
		self.rect = self.image.get_rect()
		self.rect.topleft = nx, ny
	
class Floor:
	"""The Floor class. This class is sort of like a specialized pygame Surface.\n""" \
	"""The idea is some visual elements are non-animated, non-moving and generally non-changing, \n""" \
	""" so using a class like Entity, which takes into account movement, animation and general change \n""" \
	""" would be highly ineffecient. The Floor class contains one giant image, mainly."""
	def __init__( self, tileSet, size=None, defaultTileIndex=0 ):
		self.tileSet = tileSet
		self.mass = 9999
		#A list of the rects that need to be redrawn because a Write has been performed
		self.changedAreas = []
		#Due to draw order issues, this is where the rects are sent to, then in popChangedAreas it sends changedAreas then replaces changedAreas with this for next time.
		self.nextChangedAreas = []
		
		self.imageStringBuffer = None

		self.size = size
		if size != None:
			self.mainLayer = FloorLayer( size )
			
			#Now fill the surface with the repeating default tile.

			defaultTile = tileSet.getTiles()[defaultTileIndex]
			defTileWidth = defaultTile.image.get_width()
			defTileHeight = defaultTile.image.get_height()
			

			for y in xrange( 0, self.mainLayer.image.get_height(), defTileHeight ):
				for x in xrange( 0, self.mainLayer.image.get_width(), defTileWidth ):
					self.mainLayer.image.blit( defaultTile.image, ( x, y ) )
		else:
			raise  Exception( "Floor.__init__() was called without a size" )

		self.changes = []
		self.undoneChanges = []

		#This list points to all the images used in the "floor".
		self.layers = [self.mainLayer]

		self.curLayer = 0

		self.curPan = (0, 0)

	def popChangedAreas( self ):
		"""Returns the areas changed, I don't quite remember what for.\n""" \
		"""Probably sent to the DevMenu which is in turn sent to the main-loop\n""" \
		""" to describe what areas to re-render."""
		theAreas = self.changedAreas
		self.changedAreas = self.nextChangedAreas
		self.nextChangedAreas = []
		return theAreas

	def limitChanges( self ):
		"""Prevent the list of FloorChanges stored from growing over 30."""
		overLimit = len( self.changes ) - 30
		if overLimit > 0:
			for number in xrange( overLimit ):
				self.changes.pop( number )

	def undoChange( self ):
		"""Undo a Floor edit, based on a FloorChange."""
		changeNum = len( self.changes )
		if changeNum > 0:
			theChange = self.changes.pop(changeNum - 1)
			theChangeRect = theChange.image.get_rect()
			changeWidth, changeHeight = theChangeRect.width, theChangeRect.height
			self.undoneChanges.insert( 0, self.createChange( (changeWidth, changeHeight), theChange.pos, theChange.layerNum ) )
			self.write( theChange.image, theChange.pos, theChange.layerNum, hardBlit=True )

	def redoChange( self ):
		"""Redo a Floor eidt, based on a FloorChange."""
		if len( self.undoneChanges ) > 0:
			theChange = self.undoneChanges.pop(0)
			theChangeRect = theChange.image.get_rect()
			changeWidth, changeHeight = theChangeRect.width, theChangeRect.height
			self.changes.append( self.createChange( (changeWidth, changeHeight), theChange.pos, theChange.layerNum ) )
			self.write( theChange.image, theChange.pos, theChange.layerNum, hardBlit=True )
		

	def createChange( self, area, pos, layerNum ):
		"""Generates FloorChanges from how the map currently looks at one spot, \n""" \
		"""adds the to the Floor's list of FloorChanges, then calls Floor.limitChanges."""
		tmpSurface = pygame.Surface( area )
		targetRect = tmpSurface.get_rect()
		targetRect.topleft = pos
		tmpSurface.blit( self.layers[layerNum].image, (0,0), targetRect )

	
		newChange = FloorChange( tmpSurface, pos, layerNum )
		
		return newChange

	def addUndo( self, change ):
		self.changes.append( change )
		self.limitChanges()

	def addRedo( self, change ):
		self.undoneChanges.insert( change, 0 )
		
	def write( self, image, pos, layerNum=None, hardBlit=False ):
		"""Write a given image to a certain place."""
		
		targetRect = image.get_rect()
		targetRect.topleft = pos
		
		
		if not (layerNum is None):
			destLayer = self.layers[layerNum].image
		else:
			destLayer = self.layers[self.curLayer].image

		if hardBlit:
			tmpRect = image.get_rect()
			tmpRect.topleft = pos
			destLayer.fill( pygame.Color( 0, 0, 0, 0 ), tmpRect )
		destLayer.blit( image, pos )
		self.nextChangedAreas.append( targetRect )
	
	def writeArea( self, tileIndexValue, someRect, layerNum=None, hardBlit=False ):
		"""Write one tile (selected from given tileIndexValue), all over a given area. \n """ \
		"""This blits images just as slowly as going over writeTile() a lot, but \n """ \
		"""passes one big area to self.nextChangedAreas."""
		curTile = self.tileSet.getTiles()[tileIndexValue]

		height = curTile.rect.h
		width = curTile.rect.w

		self.undoneChanges = []
		self.addUndo( self.createChange( ( someRect.width, someRect.height ), someRect.topleft, layerNum ) )

		if not (layerNum is None):
			destLayer = self.layers[layerNum].image
		else:
			destLayer = self.layers[self.curLayer].image
		
		if hardBlit:
			destLayer.fill( pygame.Color( 0, 0, 0, 0 ), someRect )
		for x in xrange( someRect.topleft[0], someRect.topleft[0]+someRect.w, curTile.rect.w ):
			for y in xrange( someRect.topleft[1], someRect.topleft[1]+someRect.h, curTile.rect.h ):
				destLayer.blit( curTile.image, (x,y) )
		self.nextChangedAreas.append( someRect )

	def writeTile( self, tileIndexValue, pos, hardBlit=False ):
		"""Write on tile (selected from given tileIndex, to a given position."""
		theTile = self.tileSet.getTiles()[tileIndexValue]
		self.addUndo( self.createChange( ( theTile.rect.w, theTile.rect.h ), pos, layerNum ) )
		self.write( theTile.image, pos, hardBlit )

	def update( self, panX, panY ):
		for each in self.layers:
			each.rect.topleft = ( each.rect.left-self.curPan[0]+panX, each.rect.top-self.curPan[1]+panY )
		self.curPan = (panX, panY)
