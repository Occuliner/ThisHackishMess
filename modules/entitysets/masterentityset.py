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
        for eachKey, eachVal in self.individualSets.item():
            for eachEnt in eachVal:
                returnDict[eachEnt.__name__] = eachEnt
        return returnDict

    def updateEnts( self ):
        for eachClass in self.entsToLoad:
            self.addEnt( eachClass )
            self.entsToLoad.remove( eachClass )

