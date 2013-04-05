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

import math

class Vector:
    def __init__( self, x = None, y = None ):
        self.x = x
        self.y = y

    def getSize( self ):
        return math.hypot( self.x, self.y )

    def __getitem__( self, key ):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        else:
            return None
            print "Invalid key for vector"
    
    def __setitem__( self, key, value ):
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value
        else:
            return None
            print "Invalid key for vector"

    def __add__( self, other ):
        classType = other.__class__
        if classType == Vector:
            return Vector( self.x + other.x, self.y + other.y )
        else:
            return None
            print "Invalid Type for Vector.__add__"

    def __sub__( self, other ):
        classType = other.__class__
        if classType == Vector:
            return Vector( self.x - other.x, self.y - other.y )
        else:
            return None
            print "Invalid Type for Vector.__sub__"

    def __mul__( self, other ):
        classType = other.__class__
        if classType in (int, float):
            return Vector( self.x*other, self.y*other )
        else:
            return None
            print "Invalid Type for Vector.__mul__"
    
    def __div__( self, other ):
        classType = other.__class__
        if classType in (int, float):
            return Vector( float(self.x)/other, float(self.y)/other )
        else:
            return None
            print "Invalid Type for Vector.__mul__"

    def setAngle( self, angle ):
        radianVal = math.radians( angle )
        curSize = self.getSize()
        return Vector( math.sin(radianVal)*curSize, math.cos(radianVal)*curSize )
            
    def getAngle( self ):
        radians = math.atan2( self.x, self.y )
        if radians < 0:
            radians += 2*math.pi
        return math.degrees( radians )
