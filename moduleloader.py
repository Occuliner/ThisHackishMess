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

"""This script provides functionality to autmomatically load modules.
This class has a few key variables, self.files is a dictionary where
 a filepath is linked to a "checksum", self.newFiles is a list of any
 files that are found by the module loader but their filepath isn't
 already a key in self.files, which means it has not loaded that module
 before. self.changedFiles is a file in self.files, but it has a different
 checksum than the one stored in self.files, which means the file has 
changed since it was loaded, and needs to be reloaded."""

import os, zlib, sys

class ModuleLoader:
    """The ModuleLoader class automates importing new and changed files whilst an
    application is running, and inserting the attributes of the modules in to a
    given set of globals and locals."""
    def __init__( self, theGlobals, theLocals, ):
        self.newFiles = []
        self.changedFiles = []
        self.files = {}
        self.globals = theGlobals
        self.locals = theLocals
    
    def searchDirectory( self, rootPathName ):
        """This method searches the directory specified with a string path,
        including directories in that dicertory. It checks for new files
        and changed files, adding them to self.changedFiles and self.newFiles
        where appropriate."""
        for pathName, dirs, fileNames in os.walk( rootPathName ):
            for eachFile in fileNames:
                filePath = os.path.join( pathName, eachFile )
                if '.py' in eachFile and not '_' in eachFile and not ".pyc" in eachFile:
                    fileData = open( filePath ).read()
                    if filePath in self.files:
                        checkSum = zlib.adler32( fileData )
                        if self.files[filePath] != checkSum:
                            self.changedFiles.append( filePath )
                            self.files[filePath] = checkSum
                    else:
                        self.files[ filePath ] = zlib.adler32( fileData )
                        self.newFiles.append( filePath )

    def pathToModuleName( self, path ):
        """This method converts a filepath string into a legal module name string.
        eg; the file modules/menuentries/button.py, to modules.menuentries.button"""
        return path.replace( os.sep, '.' ).replace( ".py", "" )
    
    def loadModules( self, path ):
        """This method takes a filepath string, puts it's through searchDirectory
        to get new files and changed files, then makes a list of all modules to
        be loaded/reloaded, and imports them."""
        self.searchDirectory( path )
        
        for eachFile in self.newFiles:
            print eachFile
            #execfile( eachFile, globals() )
            moduleName = self.pathToModuleName( eachFile )
            __import__( moduleName )
            self.globals.update( sys.modules[moduleName].__dict__ )
        
        for eachFile in self.changedFiles:
            print eachFile
            moduleName = self.pathToModuleName( eachFile )
            reload( sys.modules[moduleName] )
            self.globals.update( sys.modules[moduleName].__dict__ )
            
        self.changedFiles = []
        self.newFiles = []

#Unfortunately, when a class instance is made it is 
#defined by the class defintion at that time, so if 
# I change the class def, it doesn't modify the memory
# of the existing instances.
