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

class MasterEntitySet:
    entsToLoad = []

    def __init__( self ):
        self.individualSets = {}

        self.updateEnts()
    
    def addEnt( self, ent ):
        
        if ent.setName in self.individualSets:
            listOfNames = [ each.__name__ for each in self.individualSets[ent.setName] ]
            if ent.__name__ in listOfNames:
                self.individualSets[ent.setName][ listOfNames.index( ent.__name__ ) ] = ent
            else:
                self.individualSets[ent.setName].append( ent )
        else:
            self.individualSets[ent.setName] = [ent]
        
    def getEnts( self ):
        returnList = []
        for eachKey, eachVal in self.individualSets.items():
            returnList.extend( eachVal )
        return returnList

    def getEntDict( self ):
        returnDict = {}
        for eachKey, eachVal in self.individualSets.items():
            for eachEnt in eachVal:
                returnDict[eachEnt.__name__] = eachEnt
        return returnDict

    def updateEnts( self ):
        for eachClass in self.entsToLoad:
            self.addEnt( eachClass )
            self.entsToLoad.remove( eachClass )

