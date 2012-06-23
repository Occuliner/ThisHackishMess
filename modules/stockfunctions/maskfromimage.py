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

#Returns a booleanGrid from a given images alpha.
#Alpha parameter specifies which alpha is non-solidable
from booleangrid import *

def booleanGridFromAlpha( image, alpha=0 ):
	returnMask = []
	#for x in range( image.get_width() ):
	#	returnMask.append([])
	#	for y in range( image.get_height() ):
	#		returnMask[x].append( not image.get_at((x,y))[3]==alpha )
	
	for x in range( image.get_width() ):
		newCol = [ not image.get_at( (x,y) )[3]==alpha for y in range( image.get_height() ) ]
		returnMask.append( newCol )
	return BooleanGrid( givenGrid=returnMask )
