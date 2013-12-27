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

import extern_modules.pymunk as pymunk
import math

class AIGraphBuilder(object):
    def __init__( self, pathWidth=40, limitX=800, limitY=600 ):
        self.limitX, self.limitY = limitX, limitY
        self.pathWidth = pathWidth

    def checkForConnection( self, location1, location2, space ):

        angle = math.atan2(location1[1]-location2[1], location1[0]-location2[0])
        dAngle1 = angle-(math.pi/2.0)
        dAngle2 = angle+(math.pi/2.0)

        dx1 = (self.pathWidth/2)*math.cos(dAngle1)
        dy1 = (self.pathWidth/2)*math.sin(dAngle1)
        dx2 = (self.pathWidth/2)*math.cos(dAngle2)
        dy2 = (self.pathWidth/2)*math.sin(dAngle2)

        for eachStart in [location1, (location1[0]+dx1, location1[1]+dy1), (location1[0]-dx1, location1[1]-dy1)]:
            for eachEnd in [location2, (location2[0]+dx1, location2[1]+dy1), (location2[0]-dx1, location2[1]-dy1)]:
                queryInfos = space.segment_query(eachStart, eachEnd)
                if len(queryInfos) > 0:
                    #A collision occuried.
                    return False

        return True

    def beginSweep( self, space, graph ):
        for eachY in xrange(0, self.limitY, self.pathWidth):
            eachY = eachY + self.pathWidth/2
            for eachX in xrange(0, self.limitX, self.pathWidth):
                eachX = eachX + self.pathWidth/2
                newId = str((eachX, eachY))
                #print newId,
                graph.addNode(newId)
                # if eachX < (self.limitX-self.pathWidth/2):
                #     pass
                # if eachY < (self.limitY-self.pathWidth/2):
                #     pass

                notVeryLeft = eachX > self.pathWidth/2
                notVeryTop = eachY > self.pathWidth/2
                if notVeryLeft:
                    if self.checkForConnection( (eachX, eachY), (eachX-self.pathWidth, eachY), space ):
                        graph.connect( newId, str((eachX-self.pathWidth, eachY)) )
                        #print "connecting to", str((eachX-self.pathWidth, eachY)),
                if notVeryTop:
                    if self.checkForConnection( (eachX, eachY), (eachX, eachY-self.pathWidth), space ):
                        graph.connect( newId, str((eachX, eachY-self.pathWidth)) )
                        #print "connecting to", str((eachX, eachY-self.pathWidth)),
                if notVeryLeft and notVeryTop:
                    if self.checkForConnection( (eachX, eachY), (eachX-self.pathWidth, eachY-self.pathWidth), space ):
                        graph.connect( newId, str((eachX-self.pathWidth, eachY-self.pathWidth)) )
                        #print "connecting to", str((eachX-self.pathWidth, eachY-self.pathWidth))
                if notVeryTop and eachX < (self.limitX-self.pathWidth/2):
                    if self.checkForConnection( (eachX, eachY), (eachX+self.pathWidth, eachY-self.pathWidth), space ):
                        graph.connect( newId, str((eachX+self.pathWidth, eachY-self.pathWidth)) )
                        #print "connecting to", str((eachX+self.pathWidth, eachY-self.pathWidth)),

                #print
                #print

        #All the nodes and connections should be made now.
        #But now we should take out all the dead ends.
        graph.removeDeadEnds()