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

import math

def sliceImage( surface, tmpRect, start=0, finish=None, colourKey=None ):
    """Return subsurfces of size rect from and including the section at the 0-index up to and excluding the finish."""
    rect = tmpRect.copy()
    frames = []
    rowsize = surface.get_width()/rect.w
    startingY = math.floor( start/rowsize )*rect.h
    startingX = start%rowsize*rect.w
    if finish is not None:
        finishingY = int( math.floor( finish/rowsize ) )*rect.h
        finishingX = finish%rowsize*rect.w
    else:
        finishingY = surface.get_height()
        finishingX = surface.get_width()
        finish = (finishingY/rect.h)*rowsize
    indexCount = 0

    if startingY==finishingY:
        for x in xrange( startingX, min( surface.get_width(), finishingX ), rect.w ):
            if x + rect.w <= surface.get_width():
                rect.topleft = (x, startingY)
                tmpSurface = surface.subsurface( rect )
                tmpSurface.set_colorkey( colourKey )
                frames.append( tmpSurface )
        return frames

    for x in xrange( startingX, surface.get_width(), rect.w ):
        if x + rect.w <= surface.get_width():
            rect.topleft = (x, startingY)
            tmpSurface = surface.subsurface( rect )
            tmpSurface.set_colorkey( colourKey )
            frames.append( tmpSurface )
            indexCount += 1

    for y in xrange( int( startingY+rect.h ), min( surface.get_height(), finishingY ), rect.h ):
        if y + rect.h <= surface.get_height():
            for x in xrange( 0, surface.get_width(), rect.w ):
                if indexCount > finish-start:
                    break
                if x + rect.w <= surface.get_width():
                    rect.topleft = (x, y)
                    tmpSurface = surface.subsurface( rect )
                    tmpSurface.set_colorkey( colourKey )
                    frames.append( tmpSurface )
                    indexCount += 1
    return frames
