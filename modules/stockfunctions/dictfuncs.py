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
