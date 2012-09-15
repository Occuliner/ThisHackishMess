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

""" This module contains pre-processer classes for creating simple representations of Physics objects for use with serialization."""
import pymunk

"""I call them ghosts!"""

def vecToTuple( givenVec ):
	return ( givenVec.x, givenVec.y )

class BodyGhost:
	"""Ghost class for Pymunk bodies."""
	def __init__( self, givenBody ):
		self.mass = givenBody.mass
		self.moment = givenBody.moment
		self.angle = givenBody.angle
		self.torque = givenBody.torque
		self.position = vecToTuple( givenBody.position )
		self.velocity = vecToTuple( givenBody.velocity )
		self.velocity_limit = givenBody.velocity_limit
		self.angular_velocity = givenBody.angular_velocity
		self.angular_velocity_limit = givenBody.angular_velocity_limit
		self.force = vecToTuple( givenBody.force )
		#self.velocity_func = givenBody.velocity_func
		#self.position_func = givenBody.position_func
	def resurrect( self ):
		newBody = pymunk.Body( self.mass, self.moment)
		newBody.angle = self.angle
		newBody.torque = self.torque
		newBody.position = pymunk.vec2d.Vec2d( self.position )
		newBody.velocity = pymunk.vec2d.Vec2d( self.velocity )
		newBody.velocity_limit = self.velocity_limit
		newBody.angular_velocity = self.angular_velocity
		newBody.angular_velocity_limit = self.angular_velocity_limit
		newBody.force = pymunk.vec2d.Vec2d( self.force )
		#newBody.velocity_func = self.velocity_func
		#newBody.position_func = self.position_func
		return newBody
	def resurrectOntoGiven( self, givenBody ):
		givenBody.angle = self.angle
		givenBody.torque = self.torque
		givenBody.position = pymunk.vec2d.Vec2d( self.position )
		givenBody.velocity = pymunk.vec2d.Vec2d( self.velocity )
		givenBody.velocity_limit = self.velocity_limit
		givenBody.angular_velocity = self.angular_velocity
		givenBody.angular_velocity_limit = self.angular_velocity_limit
		givenBody.force = pymunk.vec2d.Vec2d( self.force )

class ShapeGhost:
	"""Generic ghost class that all ShapeGhost types will extend."""
	def __init__( self, givenShape ):
		#self.body = BodyGhost( givenShape.body )
		self.bodyId = id( givenShape.body )
		self.id = id( givenShape )
		self.sensor = givenShape.sensor
		self.collision_type = givenShape.collision_type
		self.group = givenShape.group
		self.layers = givenShape.layers
		self.elasticity = givenShape.elasticity
		self.friction = givenShape.friction
		self.surface_velocity = vecToTuple( givenShape.surface_velocity )
	def resurrectOntoGiven( self, givenNew ):
		#This doesn't resurrect the body, it usually happens before this
		givenNew.sensor = self.sensor
		givenNew.collision_type = self.collision_type
		givenNew.group = self.group
		givenNew.layers= self.layers
		givenNew.elasticity = self.elasticity
		givenNew.friction = self.friction
		givenNew.surface_velocity = pymunk.vec2d.Vec2d( self.surface_velocity )
	
class PolyGhost( ShapeGhost ):
	"""Ghost class for Pymunk's Poly class."""
	def __init__( self, givenPoly ):
		ShapeGhost.__init__( self, givenPoly )
		dp = givenPoly.body.position
		self.points = [ vecToTuple( eachPoint-dp ) for eachPoint in givenPoly.get_points() ]
	def resurrect( self, bodyDict ):
		newBody = bodyDict[self.bodyId]
		newPoly = pymunk.Poly( newBody, self.points )
		self.resurrectOntoGiven( newPoly )
		return newPoly

class SegmentGhost( ShapeGhost ):
	"""Ghost class for Pymunk's Segment class."""
	def __init__( self, givenSegment ):
		ShapeGhost.__init__( self, givenSegment )
		self.radius  = givenSegment.radius
		self.a, self.b = vecToTuple( givenSegment.a ), vecToTuple( givenSegment.b )
	def resurrect( self, bodyDict ):
		newBody = bodyDict[self.bodyId]
		newSegment = pymunk.Segment( newBody, self.a, self.b, self.radius )
		self.resurrectOntoGiven( newSegment )
		return newSegment

class CircleGhost( ShapeGhost ):
	"""Ghost class for Pymunk's Circle class."""
	def __init__( self, givenCircle ):
		ShapeGhost.__init__( self, givenCircle )
		self.radius  = givenCircle.radius
	def resurrect( self, bodyDict ):
		newBody = bodyDict[self.bodyId]
		newCircle = pymunk.Circle( newBody, self.radius )
		self.resurrectOntoGiven( newCircle )
		return newCircle

class SpaceGhost:
	"""I can't believe I have a class called this."""
	def __init__( self, givenSpace, boundaryBody ):
		self.gravity = vecToTuple( givenSpace.gravity )
		self.damping = givenSpace.damping
		self.shapes = []
		self.staticShapes = []
		self.bodies = { id(boundaryBody):BodyGhost( boundaryBody ) }
		self.boundaryId = id(boundaryBody)
		for eachBody in givenSpace.bodies:
			self.bodies[id(eachBody)] = BodyGhost( eachBody )
		for eachShape in givenSpace.shapes:
			if type( eachShape ) == pymunk.Poly:
				self.shapes.append( PolyGhost( eachShape ) )
			elif type( eachShape ) == pymunk.Segment:
				self.shapes.append( SegmentGhost( eachShape ) )
			elif type( eachShape ) == pymunk.Circle:
				self.shapes.append( CircleGhost( eachShape ) )
			else:
				print "SpaceGhost doesn't store type: " + eachShape.__class__.__name__,
				print ". Consider implementing a Ghost class for it."
		for eachShape in givenSpace.static_shapes:
			if type( eachShape ) == pymunk.Poly:
				self.staticShapes.append( PolyGhost( eachShape ) )
			elif type( eachShape ) == pymunk.Segment:
				self.staticShapes.append( SegmentGhost( eachShape ) )
			elif type( eachShape ) == pymunk.Circle:
				self.shape.append( CircleGhost( eachShape ) )
			else:
				print "SpaceGhost doesn't store type: " + eachShape.__class__.__name__,
				print ". Consider implementing a Ghost class for it."
	def resurrect( self ):
		newSpace = pymunk.Space()
		newSpace.gravity = self.gravity
		newSpace.damping = self.damping
		newBodyDict = {}
		newShapeDict = {}
		for key, val in self.bodies.items():
			newBodyDict[key] = val.resurrect()
		newSpace.add( [ eachVal for eachKey, eachVal in newBodyDict.items() if eachKey != self.boundaryId ] )
		for eachShape in self.shapes:
			newShape = eachShape.resurrect( newBodyDict )
			newSpace.add( newShape )
			newShapeDict[eachShape.id] = newShape
		for eachShape in self.staticShapes:
			newShape = eachShape.resurrect( newBodyDict )
			newSpace.add_static( newShape )
			newShapeDict[eachShape.id] = newShape
		return newSpace, newBodyDict, newShapeDict
