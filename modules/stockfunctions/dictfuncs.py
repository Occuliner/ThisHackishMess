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

#This method is for finding a dict entry with the numerically closest key to certain value, where that value is within the bounds of the smallest adn largest key.

def getClosestInBounds( dictionary, key ):
    return dictionary.get( getClosestKey( dictionary, key ) )

def getClosestKey( dictionary, key ):
    keys = sorted( dictionary.keys() )
    if len( keys ) == 0:
        return None
    if not( key > min( keys ) and key < max( keys ) ):
        #Key not in bounds, return none.
        return None
    closest = None
    #Should be big enough.
    delta = 9e99
    for eachKey in keys:
        thisDelta = abs( eachKey - key )
        if thisDelta < delta:
            delta = thisDelta
            closest = eachKey
    return closest

def getSurroundingKeys( dictionary, key ):
    keys = sorted( dictionary.keys() )
    if len( keys ) < 2:
        #print "Too few keys"
        return None, None
    if not( key > min( keys ) and key < max( keys ) ):
        #print "Key not in bounds, return none."
        return None, None
    #Need to find the value just before, or equal to the key.
    firstIndex = None
    startRangeIndex = 0
    endRangeIndex = len(keys)-1
    while (endRangeIndex-startRangeIndex) > 1:
        midPoint = (startRangeIndex+endRangeIndex)/2
        if keys[midPoint] > key:
            endRangeIndex = midPoint
        else:
            startRangeIndex = midPoint
    return keys[startRangeIndex], keys[endRangeIndex]

def getSurroundingValues( dictionary, key ):
    firstKey, secondKey = getSurroundingKeys( dictionary, key )
    if firstKey == None or secondKey == None:
        return None, None
    return dictionary[firstKey], dictionary[secondKey]
    
def getInterpolatedValue( dictionary, key, debugPrint=False ):
    firstKey, secondKey = getSurroundingKeys( dictionary, key )
    if firstKey == None or secondKey == None:
        return None
    ratio = float(key-firstKey)/(secondKey-firstKey)
    firstValue = dictionary[firstKey]
    secondValue = dictionary[secondKey]
    resultValue = (1.0-ratio)*firstValue+ratio*secondValue
    #if debugPrint:
    #    print firstKey, secondKey, 
    #print firstValue, secondValue, resultValue,
    return resultValue

def getInterpolatedPairValue( dictionary, key ):
    dict1 = dict( [ (eachKey, dictionary[eachKey][0]) for eachKey in dictionary.keys() ] )
    dict2 = dict( [ (eachKey, dictionary[eachKey][1]) for eachKey in dictionary.keys() ] )
    result = getInterpolatedValue( dict1, key ), getInterpolatedValue( dict2, key )
    if not (None in result):
        return result

def filterDict( dictionary, expression ):
    return dict( [(eachKey, dictionary[eachKey]) for eachKey in dictionary.keys() if expression(eachKey) ] )
