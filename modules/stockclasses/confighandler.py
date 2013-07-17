import sys, os

class ConfigHandler:
    def __init__( self, fileName, debug=False ):
        self.fileName = fileName
        #self.fileText = open( 'thm.cfg', 'r' ).readlines()
        self.debug = debug
        self.configVals = dict()
        self.defaults = { 'screen_width':'800', 'screen_height':'600', 'fullscreen':'False', 'caption':'ThisHackishMess' }

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
        return result

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
            
