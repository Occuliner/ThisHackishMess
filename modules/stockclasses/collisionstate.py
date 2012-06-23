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

def ifAccelEscapes( accel1, accel2 ):
	if accel1*accel2 < 0 and accel1 < 0:
		return True
	elif accel1*accel2 < 0:
		return False
	if accel1 <= accel2:
		return True
	else:
		return False

def momentumXCompare( obj1, obj2 ):
	return momentumCompare( obj1, obj2, 0 )

def momentumYCompare( obj1, obj2 ):
	return momentumCompare( obj1, obj2, 1 )

def momentumCompare( obj1, obj2, axis ):
	if abs(obj1.velocity[axis]) < 1:
		obj1M = obj1.mass
	else:
		obj1M = abs(obj1.getMomentumOnAxis(axis))
	if abs(obj2.velocity[axis]) < 1:
		obj2M = obj2.mass
	else:
		obj2M = abs(obj2.getMomentumOnAxis(axis))
	return cmp( obj2M, obj1M )

class Collision:
	def __init__( self, axis ):
		self.objects = []
		self.axis = axis
		# self.axis = 1

	def sortByAxis( self ):
		self.objects = sorted( self.objects, cmp=lambda x, y: cmp( x.position[self.axis], y.position[self.axis] ) )

	def sortedByMomentum( self ):
		return sorted( self.objects, cmp=lambda x, y: cmp( x.mass*x.velocity[self.axis], y.mass*y.velocity[self.axis] ) )

	def add( self, someObject ):
		self.objects.append( someObject )

	def getMomentum( self ):
		#return [ sum( [ obj.mass*obj.velocity[0] for obj in self.objects ] ), sum( [obj.mass*obj.velocity[1] for obj in self.objects ] ) ]
		return sum( [obj.mass*obj.velocity[self.axis] for obj in self.objects] )

	def getMass( self ):
		return sum( [ obj.mass for obj in self.objects ] )

	def getCentre( self ):
		return reduce( lambda x, y: [float(x[0]+y[0])/2, float(x[1]+y[1])/2], [ eachObj.center for eachObj in self.objects ] )

	def distributeForce( self, startIndex, endIndex ):
		if startIndex == endIndex:
			#print "SHIT"
			return None
		listOfObjs = [ self.objects[num] for num in xrange( startIndex, endIndex ) ]
		#if len(listOfObjs) > 1:
		#	print len(listOfObjs)
		#print startIndex, endIndex
		totalForce = sum( [ obj.mass*obj.acceleration[self.axis] for obj in listOfObjs ] )
		#print totalForce
		endAccel = totalForce/sum( [ obj.mass for obj in listOfObjs ] )
		#print endAccel
		#someNum = 0
		for eachObj in listOfObjs:
		#	print someNum
		#	someNum += 1
			eachObj.acceleration[self.axis] = endAccel

	def applyCollision( self ):
		momentum = self.getMomentum()
		mass = self.getMass()
		#centre = self.getCentre()
		newVelocity = float(momentum)/mass
		self.sortByAxis()
		
		momentumList = self.sortedByMomentum()
		
		#startOfPushGroup = 0
		#endOfPushGroup = 0
		#lastAccel = -99999
		#for eachIndex in xrange( 0, len( self.objects ) ):
		#	eachObj = self.objects[eachIndex]
		#	eachObj.velocity[self.axis] = newVelocity
		#	endOfPushGroup = eachIndex
		#	if ifAccelEscapes( lastAccel, eachObj.acceleration[self.axis] ):
		#		self.distributeForce( startOfPushGroup, endOfPushGroup )
		#		startOfPushGroup = eachIndex
		#	lastAccel = eachObj.acceleration[self.axis]
		#endOfPushGroup += 1
		#self.distributeForce( startOfPushGroup, endOfPushGroup )

class CollisionState:
	def __init__( self ):
		self.collisionXDict = {}
		self.collisionYDict = {}
		self.collisionXObjects = set([])
		self.collisionYObjects = set([])
	
	def addCollision( self, object1, object2, clippedArea ):
		# Check if this is a "valid" collision. ie if due to the velocities, the objects will cease colliding on their own.
		signX = cmp( object1.position[0], object2.position[0] )
		signY = cmp( object1.position[1], object2.position[1] )
		if object1.velocity[0]*signX > abs(object2.velocity[0]):
			return None
		if object1.velocity[1]*signY > abs(object2.velocity[1]):
			return None
		if -object2.velocity[0]*signX > abs(object1.velocity[1]):
			return None
		if -object2.velocity[1]*signY > abs(object1.velocity[1]):
			return None

		if clippedArea.width < clippedArea.height:
			if not self.collisionXDict.has_key( id(object1) ):
				self.collisionXDict[id(object1)] = []
			if not self.collisionXDict.has_key( id(object2) ):
				self.collisionXDict[id(object2)] = []
			self.collisionXDict[id(object1)].append( (object2, clippedArea) )
			self.collisionXDict[id(object2)].append( (object1, clippedArea) )
			self.collisionXObjects.add( object1 )
			self.collisionXObjects.add( object2 )
		else:
			if not self.collisionYDict.has_key( id(object1) ):
				self.collisionYDict[id(object1)] = []
			if not self.collisionYDict.has_key( id(object2) ):
				self.collisionYDict[id(object2)] = []
			self.collisionYDict[id(object1)].append( (object2, clippedArea) )
			self.collisionYDict[id(object2)].append( (object1, clippedArea) )
			self.collisionYObjects.add( object1 )
			self.collisionYObjects.add( object2 )
		#print self.collisionDict

	def sortCollisionObjects( self ):
		return sorted( self.collisionObjects, cmp=lambda x, y: cmp( x.mass*x.getVelocitySize(), y.mass*y.getVelocitySize() ) )

	def traverse( self, someObj, collision, grandDict, grandList ):
		#print grandDict
		#print collision.objects
		#print id(someObj) in grandDict
		collision.add( someObj )
		grandList.remove( someObj )
		#print grandList
		traverseThese = grandDict[id(someObj)]
		grandDict.pop( id(someObj) )
		for eachObj, clippedArea in traverseThese:
			if grandDict.has_key(id(eachObj)):
				self.traverse( eachObj, collision, grandDict, grandList )
		
	def createCollisions( self, givenDict, givenList, axis ):
		listOfCollisionObjects = list( givenList )
		theDictionary = dict( givenDict )
		listOfCollisions = []
		while len(listOfCollisionObjects) > 0:
			curObj = listOfCollisionObjects[0]
			newCollision = Collision( axis )
			self.traverse( curObj, newCollision, theDictionary, listOfCollisionObjects )
			listOfCollisions.append( newCollision )
			#print len( listOfCollisionObjects )
		return listOfCollisions

	def sortedByMomentumOnAxis( self, givenList, axis ):
		#return sorted( givenList, cmp=lambda x, y: cmp( y.mass*abs(y.velocity[axis]), x.mass*abs(x.velocity[axis]) ) )
		if axis == 0:
			return sorted( givenList, cmp=momentumXCompare )
		else:
			return sorted( givenList, cmp=momentumYCompare )

	def sortedByAxis( self, givenList, axis ):
		return sorted( givenList, cmp=lambda x, y: cmp( x.position[axis], y.position[axis] ) )

	def applyCollisions( self ):
		#allTheYCollisions = self.createCollisions( self.collisionYDict, self.collisionYObjects, 1 )
		#allTheXCollisions = self.createCollisions( self.collisionXDict, self.collisionXObjects, 0 )
		
		#for each in allTheXCollisions+allTheYCollisions:
		#	each.applyCollision()
		if self.collisionXObjects != set([]):

			totalMomentum = sum([ eachObj.getMomentumOnAxis(0) for eachObj in self.collisionXObjects ])
			newVel = float(totalMomentum)/sum([ eachObj.mass for eachObj in self.collisionXObjects ])
			#for eachObj in self.collisionXObjects:
			#	eachObj.velocity[0] = newVel

			xByMomentum = self.sortedByMomentumOnAxis( self.collisionXObjects, 0 )
			xByLocation = self.sortedByAxis( self.collisionXObjects, 0 )
			getXTurningPointIndex = xByLocation.index( xByMomentum[0] )
			for eachObj in [ xByLocation[num] for num in range( getXTurningPointIndex -1, -1, -1 ) ]:
				for eachOtherObj, eachClip in self.collisionXDict[id(eachObj)]:
					if eachOtherObj.position[0] > eachObj.position[0]:
						eachObj.pushed[0] -= eachClip.width + eachOtherObj.pushed[0]
						eachObj.position[0] += eachObj.pushed[0]
				#print self.collisionXDict[id(eachObj)]
				#eachObj.position[0] -= self.collisionXDict[id(eachObj)][1].width
			for eachObj in [ xByLocation[num] for num in range( getXTurningPointIndex+1, len(xByLocation) ) ]:
				for eachOtherObj, eachClip in self.collisionXDict[id(eachObj)]:
					if eachOtherObj.position[0] < eachObj.position[0]:
						eachObj.pushed[0] += eachClip.width + eachOtherObj.pushed[0]
						eachObj.position[0] += eachObj.pushed[0]
				#print self.collisionXDict[id(eachObj)]
				#eachObj.position[0] += self.collisionXDict[id(eachObj)][1].width

		if self.collisionYObjects != set([]):

			totalMomentum = sum([ eachObj.getMomentumOnAxis(1) for eachObj in self.collisionYObjects ])
			newVel = float(totalMomentum)/sum([ eachObj.mass for eachObj in self.collisionYObjects ])
			#for eachObj in self.collisionYObjects:
			#	eachObj.velocity[1] = newVel

			yByMomentum = self.sortedByMomentumOnAxis( self.collisionYObjects, 1 )
			yByLocation = self.sortedByAxis( self.collisionYObjects, 1 )
			getYTurningPointIndex = yByLocation.index( yByMomentum[0] )
			for eachObj in [ yByLocation[num] for num in range( getYTurningPointIndex ) ]:
				#eachObj.position[1] -= self.collisionYDict[id(eachObj)][1].height
				for eachOtherObj, eachClip in self.collisionYDict[id(eachObj)]:
					if eachOtherObj.position[1] > eachObj.position[1]:
						eachObj.pushed[1] -= eachClip.height + eachOtherObj.pushed[1]
						eachObj.position[1] += eachObj.pushed[1]
			for eachObj in [ yByLocation[num] for num in range( getYTurningPointIndex+1, len(yByLocation) ) ]:
				#print "Yay"
				for eachOtherObj, eachClip in self.collisionYDict[id(eachObj)]:
					if eachOtherObj.position[1] < eachObj.position[1]:
						eachObj.pushed[1] += eachClip.height + eachOtherObj.pushed[1]
						eachObj.position[1] += eachObj.pushed[1]



			#for eachObj in [ yByLocation[num] for num in range( getYTurningPointIndex+1, len(yByLocation) ) ]:
			#	eachObj.position[1] += self.collisionYDict[id(eachObj)][1].height
