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
#from pygame.locals import *

from booleangrid import BooleanGrid

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
	"""It is created with a given position, image, kickUp boolean and solid boolean.\n""" \
	"""Each of those attributes specifies what USED to be true of that given spot.\n""" \
	"""This is for use in undo/redo."""
	def __init__( self, image, pos, kickUp, solid ):
		#What the Floor used to look like at that spot.
		self.image = image
		self.pos = pos
		#What the KickUp used to be.
		self.kickUp = kickUp
		#If it used to be Solid.
		self.solid = solid
	
class Floor:
	"""The Floor class. This class is sort of like a specialized pygame Surface.\n""" \
	"""The idea is some visual elements are non-animated, non-moving and generally non-changing, \n""" \
	""" so using a class like Entity, which takes into account movement, animation and general change \n""" \
	""" would be highly ineffecient. The Floor class contains one giant image, one giant BooleanGrid for where \n""" \
	""" it is collidable and one giant BooleanGrid for where kickUp can occur. So you can generally think \n""" \
	""" of the Floor class as describing, the floor."""
	def __init__( self, tileSet, size=None, sourceImage=None, kickUpMap=None, solidMap=None, defaultTileIndex=0 ):
		self.tileSet = tileSet
		self.mass = 9999
		#A list of the rects that need to be redrawn because a Write has been performed
		self.changedAreas = []
		#Due to draw order issues, this is where the rects are sent to, then in popChangedAreas it sends changedAreas then replaces changedAreas with this for next time.
		self.nextChangedAreas = []
		
		self.imageStringBuffer = None

		self.size = size
		if size != None:
			self.image = pygame.Surface( size )
			#self.kickUpMap = pygame.Surface( size )
			#self.solidMap = pygame.Surface( size )
			self.kickUpMap = BooleanGrid( size[0], size[1] )
			self.solidMap = BooleanGrid( size[0], size[1] )
			
			
			#Now fill the surface with the repeating default tile.

			defaultTile = tileSet.getTiles()[defaultTileIndex]
			defTileWidth = defaultTile.image.get_width()
			defTileHeight = defaultTile.image.get_height()
			
			#gridWidth = self.image.w/defTileWidth
			#gridHeight = self.image.h/defTileHeight

			for y in xrange( 0, self.image.get_height(), defTileHeight ):
				for x in xrange( 0, self.image.get_width(), defTileWidth ):
					self.image.blit( defaultTile.image, ( x, y ) )

			#Now fill the kickUpMap if needed.
			if defaultTile.kickUp:
				#self.kickUpMap.fill( pygame.Color( 255, 255, 255 ) )
				self.kickUpMap.fill( False )

			#Never assume that it's solid. So leave the solidMap alone. IF IT IS SOLID, ERROR HARD.
			if defaultTile.solid:
				raise Exception("Floor.__init__(); DefaultTile CANNOT be solid.")

		elif sourceImage != None:
			self.image = sourceImage
			self.size = ( self.image.w, self.image.h )
			if kickUpMap != None:
				self.kickUpMap = kickUpMap
			else:
				self.KickUpMap = BooleanGrid( self.image.w, self.image.h )

			if solidMap != None:
				self.solidMap = solidMap
			else:
				self.solidMap = BooleanGrid( self.image.w, self.image.h )

				

		else:
			raise  Exception( "Floor.__init__() was called without a size or sourceImage." )

		self.changes = []
		self.undoneChanges = []

	def popChangedAreas( self ):
		"""Returns the areas changed, I don't quite remember what for.\n""" \
		"""Probably sent to the DevMenu which is in turn sent to the main-loop\n""" \
		""" to describe what areas to re-render."""
		theAreas = self.changedAreas
		self.changedAreas = self.nextChangedAreas
		self.nextChangedAreas = []
		#if theAreas != []:
		#	print theAreas
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
		#print changeNum
		if changeNum > 0:
			theChange = self.changes.pop(changeNum - 1)
			theChangeRect = theChange.image.get_rect()
			changeWidth, changeHeight = theChangeRect.width, theChangeRect.height
			self.undoneChanges.insert( 0, self.createChange( (changeWidth, changeHeight), theChange.pos, theChange.kickUp, theChange.solid) )
			#print theChange.pos, theChange.image.get_rect()
			self.write( theChange.image, theChange.pos, theChange.kickUp, theChange.solid )
			#self.writeAreaImage( theChange.image, theChange.kickUp, theChange.solid, theChange.image.get_rect()

	def redoChange( self ):
		"""Redo a Floor eidt, based on a FloorChange."""
		if len( self.undoneChanges ) > 0:
			theChange = self.undoneChanges.pop(0)
			theChangeRect = theChange.image.get_rect()
			changeWidth, changeHeight = theChangeRect.width, theChangeRect.height
			self.changes.append( self.createChange( (changeWidth, changeHeight), theChange.pos, theChange.kickUp, theChange.solid) )
			self.write( theChange.image, theChange.pos, theChange.kickUp, theChange.solid )
		

	def createChange( self, area, pos, newKickUp, newSolid ):
		"""Generates FloorChanges from how the map currently looks at one spot, \n""" \
		"""adds the to the Floor's list of FloorChanges, then calls Floor.limitChanges."""
		tmpSurface = pygame.Surface( area )
		targetRect = tmpSurface.get_rect()
		targetRect.topleft = pos
		tmpSurface.blit( self.image, (0,0), targetRect )

		if newKickUp:
			floorChangeKickUp = True
		else:
			floorChangeKickUp = False

		if newSolid:
			floorChangeSolid = True
		else:
			floorChangeSolid = False
	
		newChange = FloorChange( tmpSurface, pos, floorChangeKickUp, floorChangeSolid )
		#self.changes.append( newChange )

		#self.limitChanges()
		return newChange

	def addUndo( self, change ):
		self.changes.append( change )
		self.limitChanges()

	def addRedo( self, change ):
		self.undoneChanges.insert( change, 0 )
		
	def write( self, image, pos, kickUp, solid ):
		"""Write a given image, kickUp boolean and solid boolean, to a certain place."""
		
		targetRect = image.get_rect()
		targetRect.topleft = pos
		
		self.image.blit( image, pos )
		self.kickUpMap.fill( kickUp, targetRect )

		self.solidMap.fill( solid, targetRect )

		self.nextChangedAreas.append( targetRect )
	
	def writeArea( self, tileIndexValue, someRect ):
		"""Write one tile (selected from given tileIndexValue), all over a given area. \n """ \
		"""This blits images just as slowly as going over writeTile() a lot, but edits \n """ \
		""" the kickUpMap and solidMap all in one go. And passes one big area to self.nextChangedAreas."""
		curTile = self.tileSet.getTiles()[tileIndexValue]

		height = curTile.rect.h
		width = curTile.rect.w

		self.undoneChanges = []
		self.addUndo( self.createChange( ( someRect.width, someRect.height ), someRect.topleft, curTile.kickUp, curTile.solid ) )

		for x in xrange( someRect.topleft[0], someRect.topleft[0]+someRect.w, curTile.rect.w ):
			for y in xrange( someRect.topleft[1], someRect.topleft[1]+someRect.h, curTile.rect.h ):
				#self.createChange( ( curTile.rect.w, curTile.rect.h ), (x,y), curTile.kickUp, curTile.solid )
				
				self.image.blit( curTile.image, (x,y) )

		self.kickUpMap.fill( curTile.kickUp, someRect )
		self.solidMap.fill( curTile.solid, someRect )

		self.nextChangedAreas.append( someRect )

#	def writeAreaImage( self, image, kickUp, solid, tileRect, someRect ):
#		"""Write one tile (selected from given tileIndexValue), all over a given area. \n """ \
#		"""This blits images just as slowly as going over writeTile() a lot, but edits \n """ \
#		""" the kickUpMap and solidMap all in one go. And passes one big area to self.nextChangedAreas."""
#		#curTile = self.tileSet.getTiles()[tileIndexValue]
#
#		height = tileRect.h
#		width = tileRect.w
#
#		for x in xrange( someRect.topleft[0], someRect.topleft[0]+someRect.w, tileRect.w ):
#			for y in xrange( someRect.topleft[1], someRect.topleft[1]+someRect.h, tileRect.h ):
#				#self.createChange( ( curTile.rect.w, curTile.rect.h ), (x,y), curTile.kickUp, curTile.solid )
#				
#				self.image.blit( image, (x,y) )
#
#		self.addUndo( self.createChange( ( width, height ), someRect.topleft, kickUp, solid ) )
#
#		self.kickUpMap.fill( kickUp, someRect )
#		self.solidMap.fill( solid, someRect )
#
#		self.nextChangedAreas.append( someRect )

	def writeTile( self, tileIndexValue, pos ):
		"""Write on tile (selected from given tileIndex, to a given position."""
		theTile = self.tileSet.getTiles()[tileIndexValue]
		self.addUndo( self.createChange( ( theTile.rect.w, theTile.rect.h ), pos, theTile.kickUp, theTile.solid ) )
		self.write( theTile.image, pos, theTile.kickUp, theTile.solid )

	def draw( self, surface, destPoint=( 0, 0 ) ):
		"""Blit the Floor's image to a given surface, at (0,0)."""
		surface.blit( self.image, destPoint )
