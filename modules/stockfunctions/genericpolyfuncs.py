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

#This file just contains random functions for use on polygon data.
import extern_modules.pymunk as pymunk

def getMidOfPoints( polyPoints ):
    numOf = len(polyPoints)
    midX = float(sum([ each[0] for each in polyPoints ]))/numOf
    midY = float(sum([ each[1] for each in polyPoints ]))/numOf
    return midX, midY

def getExtremesAlongAxis( polyPoints, axis, default ):
    extreme1Proj, extreme2Proj = pymunk.Vec2d(0,0), pymunk.Vec2d(0,0)
    extreme1, extreme2 =  list( default ), list( default )
    midPoint = pymunk.Vec2d( getMidOfPoints( polyPoints ) )
    if axis.y == 0:
        for eachPoint in polyPoints:
            projection = (eachPoint-midPoint).projection( axis )
            if projection.x < 0 and projection.get_length() > extreme1Proj.get_length():
                extreme1Proj = projection
                extreme1 = eachPoint
            elif projection.x > 0 and projection.get_length() > extreme2Proj.get_length():
                extreme2Proj = projection
                extreme2 = eachPoint
    else:
        for eachPoint in polyPoints:
            projection = (eachPoint-midPoint).projection( axis )
            if projection.y < 0 and projection.get_length() > extreme1Proj.get_length():
                extreme1Proj = projection
                extreme1 = eachPoint
            elif projection.y > 0 and projection.get_length() > extreme2Proj.get_length():
                extreme2Proj = projection
                extreme2 = eachPoint
    return extreme1, extreme2
