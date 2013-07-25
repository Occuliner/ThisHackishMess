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

from tile import *
#The createFromSheet function takes a tilesheet and a tile size and returns a list of subsurfaced tiles. To determine which tiles support kickup or are solid, you can use either
#the "break" parameters. Which is a list index value of which tile should be the first to go from non-solid to solid or non-kickUp to kickUp. Or you can use the list
#parameters, which is instead a list of index values of which tiles support kickUp or are solid.

def getSection( x, y, size, image ):
    theRect = pygame.Rect( ( x, y ), size )
    return image.subsurface( theRect )

class TileGroup:
    def createFromSheet( self, tileSheet, size, solidBreak = None, kickUpBreak = None, solidList = None, kickUpList = None ):
        tileList = []
        for y in xrange( 0, tileSheet.get_height(), size[1] ):
            for x in xrange( 0, tileSheet.get_width(), size[0] ):
                tileList.append( Tile( getSection( x, y, size, tileSheet ) ) )

        if solidBreak != None:
            for eachTileIndex in xrange( solidBreak, len( tileList ) ):
                tileList[eachTileIndex].solid = True

        elif solidList != None:
            for eachTileIndex in solidList:
                tileList[eachTileIndex].solid = True

        else:
            raise Exception("splitToTiles() was called without a solidBreak or solidList parameter.")
    
        if kickUpBreak != None:
            for eachTileIndex in xrange( kickUpBreak, len( tileList ) ):
                tileList[eachTileIndex].kickUp = True
    
        elif kickUpList != None:
            for eachTileIndex in kickUpList:
                tileList[eachTileIndex].kickUp = True
    
        else:
            raise Exception("splitToTiles() was called without a solidBreak or solidLis parameter.")
    
        return tileList

