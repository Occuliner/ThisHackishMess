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

#This file just contains random functions for use on polygon data.
import extern_modules.pymunk as pymunk

def getMidOfPoints( polyPoints ):
	numOf = len(polyPoints)
	midX = float(sum([ each[0] for each in polyPoints ]))/numOf
	midY = float(sum([ each[1] for each in polyPoints ]))/numOf
	return midX, midY

def getExtremesAlongAxis( polyPoints, axis, default ):
	extreme1Proj, extreme2Proj = pymunk.Vec2d(0,0), pymunk.Vec2d(0,0)
	extreme1, extreme2 =  list( default ), list( default )
	midPoint = pymunk.Vec2d( getMidOfPoints( polyPoints ) )
	if eachEnt.body.velocity.y == 0:
		for eachPoint in polyPoints:
			projection = (eachPoint-midPoint).projection( axis )
			if projection.x < 0 and projection.get_length() > extreme1Proj.get_length():
				extreme1Proj = projection
				extreme1 = eachPoint
			elif projection.x > 0 and projection.get_length() > extreme2Proj.get_length():
				extreme2Porj = projection
				extreme2 = eachPoint
	else:
		for eachPoint in polyPoints:
			projection = (eachPoint-midPoint).projection( axis )
			if projection.y < 0 and projection.get_length() > extreme1Proj.get_length():
				extreme1Proj = projection
				extreme1 = eachPoint
			elif projection.y > 0 and projection.get_length() > extreme2Proj.get_length():
				extreme2Porj = projection
				extreme2 = eachPoint
	return extreme1, extreme2
