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
