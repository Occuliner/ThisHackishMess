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

"""This class is a simple class for drawing out lines over the playState for use with the DevMenu and physics-visualisation mode."""

import pygame, extern_modules.pymunk as pymunk

red = pygame.Color( 255, 0, 0 )
blue = pygame.Color( 0, 0, 255 )

class LineVisualiser:
    def __init__( self, playState ):
        self.devMenuLineGroups = []
        self.renderLines = False
        self.renderPhysicsLines = False
        self.playState = playState
        self.flush = False
        self.forceNoRender = False
        self.oldRects = []

    def drawLinesWithPoints( self, surface, listOfPoints, pointRender=False, lineColour=red, pointColour=blue, dest=(0, 0) ):
        listOfPoints = [ ( each[0]+dest[0], each[1]+dest[1] ) for each in listOfPoints ]
        updateRects = []
        updateRects.append( pygame.draw.lines( surface, lineColour, True, listOfPoints ) )
        if pointRender:
            for eachPoint in listOfPoints:
                updateRects.append( pygame.draw.rect( surface, pointColour, pygame.Rect( eachPoint[0]-2, eachPoint[1]-2, 4, 4 ) ) )
        return updateRects

    def drawCircle( self, surface, radius, center, lineColour=red, dest=(0, 0) ):
        updateRects = []
        updateRects.append( pygame.draw.circle(surface, lineColour, [center[0]+dest[0], center[1]+dest[1]], int(radius), 1) )
        return updateRects

    def draw( self, surface, destPoint=(0, 0) ):
        updateRects = []
        if self.renderLines:
            for eachGroup in self.devMenuLineGroups:
                updateRects.extend( self.drawLinesWithPoints( surface, eachGroup, True ) )
                    
            if self.renderPhysicsLines:
                for eachShape in self.playState.space.shapes:
                    if type( eachShape ) == pymunk.Poly:
                        if eachShape.entity.pureSensor:
                            updateRects.extend( self.drawLinesWithPoints( surface, eachShape.get_points(), True, blue, red, destPoint ) )
                        else:
                            updateRects.extend( self.drawLinesWithPoints( surface, eachShape.get_points(), True, dest=destPoint ) )
                    elif type( eachShape ) == pymunk.Segment:
                        #updateRects.append( pygame.draw.line( surface, red, eachShape.a, eachShape.b ) )
                        updateRects.extend( self.drawLinesWithPoints( surface, [ eachShape.a, eachShape.b ], True, dest=destPoint ) )
                    
                    elif type( eachShape ) == pymunk.Circle:
                        bodyLoc = int(eachShape.body.position.x), int(eachShape.body.position.y)
                        updateRects.extend( self.drawCircle( surface, eachShape.radius, [bodyLoc[0], bodyLoc[1]], dest=destPoint ) )
                    else:
                        print "LineVisualiser doesn't render type: " + eachShape.__class__.__name__
        #Empty self.devMenuLineGroups at the end of the frame.
        if self.flush:
            self.devMenuLineGroups = []
            self.flush = False
        #Assume no renders next frame?
        if self.forceNoRender:
            self.renderLines = False
            self.renderPhysicsLines = False
            self.forceNoRender = False
        old = list( self.oldRects )
        self.oldRects = list( updateRects )
        return updateRects+old
