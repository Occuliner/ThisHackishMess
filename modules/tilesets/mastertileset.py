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
