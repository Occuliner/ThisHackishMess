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

