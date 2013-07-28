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

import math

def sliceImage( surface, tmpRect, start=0, finish=None, colourKey=None ):
    """Return subsurfces of size rect from and including the section at the 0-index up to and excluding the finish."""
    rect = tmpRect.copy()
    frames = []
    rowsize = float(surface.get_width())/rect.w
    startingY = int( math.floor( start/rowsize )*rect.h )
    startingX = int( start%rowsize*rect.w )
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
