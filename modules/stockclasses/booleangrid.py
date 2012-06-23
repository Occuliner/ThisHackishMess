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

"""Defines the BooleanGrid class"""
import pygame
class BooleanGrid:
	def __init__(self, width=None, height=None, 
			defaultValue=False, givenGrid=None):
		if givenGrid is not None:
			self.grid = givenGrid
			self.height = len( self.grid[0] )
			self.width = len( self.grid )
		else:
			self.grid = [ [ defaultValue for y in xrange( height ) ] 
					for x in xrange( width ) ]
			#self.grid = [list( [defaultValue]*height )]*width
			self.width = width
			self.height = height

	def __getitem__( self, keyVal ):
		if type( keyVal ) != int:
			raise TypeError( "Non-integer index value passed to BooleanGrid.__getitem__" )
		return self.grid[keyVal]

	def __setitem__( self, keyVal, value ):
		if type( keyVal ) != int:
			raise TypeError( "Non-integer index value passed to BooleanGrid.__setitem__" )
		self.grid[keyVal] = value

	def getListFromRect( self, someRect ):
		"""BooleanGrid.getListFromRect()\nExample: """ \
		"""someGrid.getListFromRect( someRect )\n""" \
		"""Returns a grid-list of size (someRect.width, someRect.height) \n""" \
		"""with values (x,y) = somegrid[x+someRect.left][y+someRect.top]."""
		return self.getListFromArea( someRect.topleft[0], someRect.topleft[1], someRect.w, someRect.h )

	def getListFromArea( self, x, y, w, h ):
		"""Returns a 2d-list from a given x,y,w,h area."""
		#returnGrid = []
		#for colNum in xrange( x, x+w ):
		#	returnGrid.append( self.grid[colNum][y:y+h] )
		#returnGrid = [ [ self.grid[xpoint][ypoint] for ypoint in xrange( y, y+h ) ] for xpoint in xrange( x, x+w ) ]
		returnGrid = [ self.grid[xpoint][y:y+h] for xpoint in xrange( x, x+w ) ]
		return returnGrid

	def getGridFromArea( self, x, y, w, h ):
		"""Returns a BooleanGrid from a given x,y,w,h area."""
		return BooleanGrid( givenGrid=self.getListFromArea( x, y, w, h ) )

	def getGridFromRect( self, someRect ):
		"""Returns a BooleanGrid from a given Rect area."""
		return BooleanGrid( givenGrid=self.getListFromRect( someRect ) )

	def getTrueBox( self ):
		"""
		BooleanGrid.getTrueBox()""" \
		"""Example:\n""" \
		"""	someGrid.getTrueBox()"""\
		"""\nReturns a (x, y, w, h) list where x is the left-most instance """ \
		"""of True in someGrid, w is the difference between the left-most """ \
		""" and right-most, y is the top-most, and h is the difference bewteen """ \
		"""top-most and bottom-most."""
		#x1, x2, y1, y2, = self.width, -1, self.height, -1

		#for x in xrange( self.width ):
		#	for y in xrange( self.height ):
		#		if self.grid[x][y]:
		#			x1 = min( x1, x )
		#			x2 = max( x2, x )
		#			y1 = min( y1, y )
		#			y2 = min( y2, y )

		#return ( x1, y1, x2-x1, y2-y1 )

		
		y1, y2, x1, x2 = self.height, -1, self.width, -1
		for xCur in xrange( self.width ):
			#if True in [ self.grid[xCur][yPoint] for yPoint in xrange( self.height ) ]:
			if True in self.grid[xCur]:
				x1 = xCur
				break
		if x1 == self.width:
			return ( -1, -1, -1 -1 )
		for xCur in xrange( self.width - 1, -1, -1 ):
			#if True in [ self.grid[xCur][yPoint] for yPoint in xrange( self.height ) ]:
			if True in self.grid[xCur]:
				x2 = xCur
				break
		
		for yCur in xrange( self.height ):
			#if True in [ self.grid[xPoint][yCur] for xPoint in xrange( self.width ) ]:
			if True in [ col[yCur] for col in self.grid ]:
				y1 = yCur
				break
		if y1 == self.height:
			return ( -1, -1, -1, -1 )
		for yCur in xrange( self.height - 1, -1, -1 ):
			#if True in [ self.grid[xPoint][yCur] for xPoint in xrange( self.width ) ]:
			if True in [ col[yCur] for col in self.grid ]:
				y2 = yCur
				break
		
		return ( x1, y1, x2-x1+1, y2-y1+1 )
		
	def mergeWith( self, otherGrid, comparison='or' ):
		"""
		BooleanGrid.mergeWith( otherGrid, [comparison] )

		Example:
			firstGrid.mergeWith( secondGrid, [comparison] )

		Returns new BooleanGrid with each point (x,y) = True iff (firstGrid[x][y] or/and secondGrid[x][y]) Or/and is decided by the comparison string parameter.
		
		Grids must be same size.		
		"""
		
		if self.width!=otherGrid.width or self.height!=otherGrid.height:
			raise Exception( "Non-equal size grids passed to BooleanGrid.mergeWith" )
		
		if comparison == 'or':
			newGridLists = [ [ self.grid[x][y] or otherGrid.grid[x][y] for y in xrange( self.height ) ] for x in xrange( self.width ) ]
		elif comparison == 'and':
			newGridLsits = [ [ self.grid[x][y] and otherGrid.grid[x][y] for y in xrange( self.height ) ] for x in xrange( self.width ) ]
		else:
			raise Exception( "Comparison-string paramtere passed to BooleanGrid.mergeWith is not 'and' or 'or'" )
		return BooleanGrid( givenGrid=newGridLists )
		

	def fill( self, value, someRect=None ):
		"""Fills the BooleanGrid with value in area someRect
		Fills whole thing if rect not given."""
		if someRect is None:
			someRect = pygame.Rect( 0, 0, self.width, self.height )
		if type( value ) != bool:
			raise TypeError( "Non-Boolean value passed to BooleanGrid.fill()" )
		#print someRect.width, someRect.height
		
		#VERY revised system. Hopefully faster, benchmark it.
		#print someRect.topleft[0]
		for column in ( self.grid[val] for val in xrange( someRect.topleft[0], someRect.topleft[0]+someRect.w ) ):
			#print colNum
			column[ someRect.topleft[1]: someRect.topleft[1]+someRect.h ] = [value]*someRect.h
		
		#for xVal in xrange( someRect.topleft[0], someRect.topleft[0]+someRect.w ):
		#	for yVal in xrange( someRect.topleft[1], someRect.topleft[1]+someRect.h ):
				#print xVal, self.width, yVal, self.height
				#print xVal, yVal
		#		self.grid[xVal][yVal] = value
