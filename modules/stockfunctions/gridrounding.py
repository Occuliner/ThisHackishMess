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

"""This file defines the gridRound function. See it's docstring for more details."""

def gridRound( pos, w, h, roundToTopLeft=True, trueRounding=False ):
    """gridRound( pos, w, h, roundToTopLeft=True )\n""" \
    """This function rounds a given pos variable to the nearest lower or upper multiples \n""" \
    """ of w and h in their respective directions. roundToTopLeft=True means it rounds towards the topleft. \n""" \
    """ trueRounding means round to the closest corner, not topleft or bottomright."""

    xRemainder, yRemainder = pos[0]%w, pos[1]%h
    
    newPosition = [ pos[0] - xRemainder, pos[1] - yRemainder ]

    if trueRounding:
        if float(xRemainder)/w > 0.5:
            newPosition[0] += w
        if float(yRemainder)/h > 0.5:
            newPosition[1] += h
    elif not roundToTopLeft:
        newPosition[0] += w
        newPosition[1] += h
    
    return newPosition
