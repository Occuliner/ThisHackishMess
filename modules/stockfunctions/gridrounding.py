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

"""This file defines the gridRound function. See it's docstring for more details."""

def gridRound( pos, w, h, roundToTopLeft=True, trueRounding=False ):
	"""gridRound( pos, w, h, roundToTopLeft=True )\n""" \
	"""This function rounds a given pos variable to the nearest lower or upper multiples \n""" \
	""" of w and h in their respective directions. roundToTopLeft=True means it rounds towards the topleft. \n""" \
	""" trueRounding means round to the closest corning, not topleft or bottomright."""

	xRemainder, yRemainder = pos[0]%w, pos[1]%h
	
	newPosition = [ pos[0] - xRemainder, pos[1] - yRemainder ]

	if trueRounding:
		if float(xRemainder)/w > 0.5:
			newPosition[0] += w
		if float(yRemainder)/h > 0.5:
			newPosition[1] += h
	elif not roundToTopLeft:
		newPosition[0] += w
		newPosition[1] += h
	
	return newPosition
