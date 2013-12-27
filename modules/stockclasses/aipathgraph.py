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

class AIPathGraph(object):
    def __init__( self, listOfNodeIds=[] ):
        self.nodes = dict([ (each, []) for each in listOfNodeIds])

    def addNode( self, id ):
        assert self.nodes.has_key(id) == False
        self.nodes[id] = []

    def getCostOfEdge( self, id1, id2 ):
        for each in self.nodes[id1]:
            if each[0] == id2:
                return each[1]
        raise Exception("AIPathGraph.costOfEdge was given info for a non-existing edge.")

    def connect( self, id1, id2, cost=1.0, bidirectional=True ):
        self.nodes[id1].append((id2, cost))
        if bidirectional:
            self.connect(id2, id1, cost, False)

    def getNeighbours( self, id ):
        return [ each[0] for each in self.nodes[id] ]

    def canTraverse( self, id1, id2 ):
        return id2 in self.nodes[id1]

    def removeDeadEnds( self ):
        """This will get rid of any node where the length of it's list of connections is zero.
        Quite simply, if you can't go anywhere from that node, it's removed."""
        for eachKey in self.nodes.keys():
            if len(self.nodes[eachKey]) == 0:
                del self.nodes[eachKey]