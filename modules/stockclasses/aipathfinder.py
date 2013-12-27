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

def popSmallestPrior( itemList, priorTable ):
    minP = 9.9e100
    res = None
    i = None
    for eachI in xrange(len(itemList)):
        each = itemList[eachI]
        if priorTable[each] < minP:
            minP = priorTable[each]
            res = each
            i = eachI
    if i != None:
        itemList.pop(i)
    return res

class AIPathFinder(object):
    def __init__( self, graph ):
        self.graph = graph
        #Each traversal path is a tuple, first item is the dest id, second is a list of path ids.
        self.currentTraversals = []
    
    def find( self, startId, endId ):
        """Uses simple breadth-first-search to find a path in a graph, with an autocompletion-type feature based off currently active paths."""
        #First get each current path with the same dest.
        possibleOverlaps = [ each for each in self.currentTraversals if each[0] == endId ]
        result = []
        #queue = [(0.0, startId)]
        escape = False
        #Dictionary, key is id of visited node, val is pred.

        costTable = {}
        unvisited = []
        for each in self.graph.nodes.keys():
            costTable[each] = 9.9e99
            unvisited.append(each)

        costTable[startId] = 0.0
        predTable = {}
        predTable[startId] = None
        while len(unvisited) > 0:
            curId = popSmallestPrior(unvisited, costTable)
            curCost = costTable[curId]

            #If curId is endId, congrats
            if curId != endId:
                for eachPath in possibleOverlaps:
                    if curId in eachPath[1]:
                        print "Test that this short cut works"
                        #Then just use the rest of that path.
                        i = eachPath[1].index(curId)
                        rest = eachPath[1][i+1:]
                        result.extend( rest )
                        escape = True
                        break
                if escape:
                    break
                for eachId in self.graph.getNeighbours(curId):
                    eachCost = curCost+self.graph.getCostOfEdge(curId, eachId)
                    if eachCost < costTable[eachId]:
                        costTable[eachId] = eachCost
                        predTable[eachId] = curId

            else:
                break
        
        while curId != startId:
            result.insert( 0, curId )
            curId = predTable[curId]

        self.currentTraversals.append((endId, result))

        return result

    def clearTraversals( self ):
        self.currentTraversals = []