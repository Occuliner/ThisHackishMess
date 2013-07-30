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

class ConfigHandler:
    def __init__( self, fileName, debug=False ):
        self.fileName = fileName
        #self.fileText = open( 'thm.cfg', 'r' ).readlines()
        self.debug = debug
        self.configVals = dict()
        self.defaults = { 'screen_width':'800', 'screen_height':'600', 'fullscreen':'0', 'caption':'ThisHackishMess', 'dev_mode':'1' }

    def readConfig( self ):
        theFile = open( self.fileName, 'r' )
        text = theFile.readlines()
        theFile.close()
        return self.processFile( text )

    def writeConfig( self ):
        text = ""
        for eachKey, eachVal in self.configVals.iteritems():
            text += eachKey + "," + eachVal + "\n"
        theFile = open( self.fileName, "w" )
        theFile.write( text )
        theFile.close()
            
    def processFile( self, text ):
        for eachLine in text:
            vals = eachLine.split(',', 1)
            if len( vals ) == 1:
                if self.debug:
                    print "Config syntax error on line:", eachLine
            else:
                self.configVals[vals[0]] = vals[1]

    def setVal( self, key, val ):
        self.confgVals[key] = val

    def getVal( self, key ):
        if self.configVals.has_key( key ):
            return self.configVals[key]
        if self.defaults.has_key( key ):
            return self.defaults[key]
        return None

    def getWidth( self ):
        return int(self.getVal('screen_width'))

    def getHeight( self ):
        return int(self.getVal('screen_height'))
            
