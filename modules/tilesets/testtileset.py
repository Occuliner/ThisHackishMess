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

from tilegroup import *

from imageload import *

from mastertileset import *

class TestTileSet( TileGroup ):
    name = "TestTileSet"
    a = 1
    def __init__( self ):
        self.tiles = TileGroup.createFromSheet( self, loadImageNoAlpha( "testTileMap.png", 2 ), size=( 32, 16 ), kickUpBreak=1, solidList = [] )

#MasterTileSet.tileSetClasses.append( TestTileSet )
#MasterTileSet.tileSetsToLoad.append( TestTileSet )
