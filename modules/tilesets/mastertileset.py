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

from tilegroup import *

class MasterTileSet( TileGroup ):
	#tileSetClasses = []
	tileSetsToLoad = []
	def __init__( self ):
		self.individualSets = {}

		self.updateSets()

	def addSet( self, tileSet ):
		
		self.individualSets[tileSet.name] = tileSet.tiles

	def getTiles( self ):
		returnList = []
		for eachKey, eachVal in self.individualSets.items():
			returnList.extend( eachVal )
		return returnList

	def updateSets( self ):
		for eachClass in self.tileSetsToLoad:
			self.addSet( eachClass() )
			self.tileSetsToLoad.remove( eachClass )
