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

#This function returns true if mask1 and mask2 are ever true at the same spot.
def maskOverLap( mask1, mask2 ):
	mask1Width = len( mask1 )
	mask1Height = len( mask1[0] )
	mask2Width = len( mask2 )
	mask2Height = len( mask2[0] )
	if mask1Width != mask2Width or mask1Height != mask2Height:
		raise Exception( "Two different size grids passed to maskOverlap, it requires same size grids." )
	for xVal in xrange( mask1Width ):
		for yVal in xrange( mask1Heigbht ):
			if mask1[xVal][yVal] and mask2[xVal][yVal]:
				return True
	return False

	#This is another possible method, I should check which is faster.
	
	#pointsPart1 = []
	#[ pointspart1.extend( column ) for column in mask1 ]
	#pointsPart2 = []
	#[ pointspart2.extend( column ) for column in mask2 ]
	#return True in [ points[0] and points[1] for points in zip( pointsPart1, pointsPart2 ) ]
	
