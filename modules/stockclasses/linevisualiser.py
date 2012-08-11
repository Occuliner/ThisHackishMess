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

"""This class is a simple class for drawing out lines over the playState for use with the DevMenu and physics-visualisation mode."""

import pygame, pymunk

red = pygame.Color( 255, 0, 0 )
blue = pygame.Color( 0, 0, 255 )

class LineVisualiser:
	def __init__( self, playState ):
		self.devMenuLineGroups = []
		self.renderLines = False
		self.renderPhysicsLines = False
		self.playState = playState
		self.flush = False
		self.forceNoRender = False
		self.oldRects = []

	def drawLinesWithPoints( self, surface, listOfPoints, pointRender=False, lineColour=red, pointColour=blue, dest=(0, 0) ):
		listOfPoints = [ ( each[0]+dest[0], each[1]+dest[1] ) for each in listOfPoints ]
		updateRects = []
		updateRects.append( pygame.draw.lines( surface, lineColour, True, listOfPoints ) )
		if pointRender:
			for eachPoint in listOfPoints:
				updateRects.append( pygame.draw.rect( surface, pointColour, pygame.Rect( eachPoint[0]-2, eachPoint[1]-2, 4, 4 ) ) )
		return updateRects

	def drawCircle( self, surface, radius, center, lineColour=red, dest=(0, 0) ):
		updateRects = []
		updateRects.append( pygame.draw.circle(surface, lineColour, [center[0]+dest[0], center[1]+dest[1]], radius, width=1 ) )
		return updateRects

	def draw( self, surface, destPoint=(0, 0) ):
		updateRects = []
		if self.renderLines:
			for eachGroup in self.devMenuLineGroups:
				updateRects.extend( self.drawLinesWithPoints( surface, eachGroup, True ) )
					
			if self.renderPhysicsLines:
				for eachShape in self.playState.space.shapes + self.playState.space.static_shapes:
					if type( eachShape ) == pymunk.Poly:
						if eachShape.entity.pureSensor:
							updateRects.extend( self.drawLinesWithPoints( surface, eachShape.get_points(), True, blue, red, destPoint ) )
						else:
							updateRects.extend( self.drawLinesWithPoints( surface, eachShape.get_points(), True, dest=destPoint ) )
					elif type( eachShape ) == pymunk.Segment:
						#updateRects.append( pygame.draw.line( surface, red, eachShape.a, eachShape.b ) )
						updateRects.extend( self.drawLinesWithPoints( surface, [ eachShape.a, eachShape.b ], True, dest=destPoint ) )
					
					elif type( eachShape ) == pymunk.Circle:
						bodyLoc = eachShape.body.position.x, eachShape.body.position.y
						updateRects.extend( self.drawCircle( surface, eachShape.radius, [bodyLoc[0]+eachShape.radius, bodyLoc[1]+eachShape.radius], dest=destPoint ) )
					else:
						print "LineVisualiser doesn't render type: " + eachShape.__class__.__name__
		#Empty self.devMenuLineGroups at the end of the frame.
		if self.flush:
			self.devMenuLineGroups = []
			self.flush = False
		#Assume no renders next frame?
		if self.forceNoRender:
			self.renderLines = False
			self.renderPhysicsLines = False
			self.forceNoRender = False
		old = list( self.oldRects )
		self.oldRects = list( updateRects )
		return updateRects+old
