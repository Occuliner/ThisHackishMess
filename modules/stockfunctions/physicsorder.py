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

import random

def physicsOrder( object1, object2 ):
	if object1.stability > object2.stability:
		return [object1, object2]
	elif object1.stability < object2.stability:
		return [object2, object1]
	else:
		if object1.velocity[0]**2+object1.velocity[1]**2 > object2.velocity[0]**2+object2.velocity[1]**2:
			return [object1, object2]
		elif object1.velocity[0]**2+object1.velocity[1]**2 < object2.velocity[0]**2+object2.velocity[1]**2:
			return [object2, object1]
		else:
			if random.randint( 0, 1 ) == 0:
				return [object1, object2]
			else:
				return [object2, object1]
