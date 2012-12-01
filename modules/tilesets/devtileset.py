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

from imageload import *

from mastertileset import *

import pygame

class DevDraftSet( TileGroup ):
	name = "DevDraftSet"
	a = 1
	def __init__( self ):
		sheetImage = loadImageNoAlpha( "devtileset.png", 2 )
		sheetImage.set_colorkey( pygame.Color( 255, 0, 255 ) )
		self.tiles = TileGroup.createFromSheet( self, sheetImage, size=( 40, 40 ), kickUpBreak=1, solidList = [] )

MasterTileSet.tileSetsToLoad.append( DevDraftSet )
