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

import sys, os

class MasterEntitySet:
    entsToLoad = []

    def __init__( self ):
        self.entityDefs = {}

    def getEntityClass( self, className ):
        classDef = self.entityDefs.get( className )
        if classDef is not None:
            return classDef
        self.importClass( className )
	classDef = self.entityDefs.get( className )
        if classDef is not None:
            return classDef

    def importClass( self, className ):
        moduleName = "modules.entitysets." + "_" + className.lower()
        __import__( moduleName )
           
        #self.entityDefs.update( sys.modules[moduleName].__dict__ )
        for eachClass in MasterEntitySet.entsToLoad:
            self.entityDefs[eachClass.__name__] = eachClass
        MasterEntitySet.entsToLoad = []
        
    
    def getEnts( self ):
	return self.entityDefs.values()

    def loadAllEnts( self ):
        listOfNames = os.listdir( os.path.join( 'modules', 'entitysets', ) )
	listOfNames = [ each for each in listOfNames if ( each[0] == "_" and each[-3:] == ".py" and each[:2] != "__" ) ]
        listOfNames = [ each.replace(".py", "").replace("_", "") for each in listOfNames ]
        
        for eachName in listOfNames:
            self.importClass( eachName )

