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

import extern_modules.pygnetic as pygnetic, networkhandlers, weakref, extern_modules.pymunk as pymunk

class NetworkClient:
	def __init__( self, playState=None, networkEntsClassDefs=None, conn_limit=1, networkingMode=0, clientSidePrediction=True, resimulationMethod=1, *args, **kwargs ):
		self._client = pygnetic.Client( conn_limit, *args, **kwargs )
		
		self.playStateRef = weakref.ref( playState )

		self.networkTick = None

		self.networkEntsClassDefs = networkEntsClassDefs

		self.handler = None

		self.name = "Banana"

		self.connection = None

		self.timer = 0.0

		#Networking mode is whether the client will merely recreate the state as sent from the host, and send input, or use interpolation and/or extrapolation.
		#0=No interoplation/extrapoltion, 1=Extrapolation, 2=Interpolation.
		self.interpolationOn, self.extrapolationOn = False, False
		if networkingMode is 1:
			self.extrapolationOn = True
		elif networkingMode is 2:
			self.interpolationOn = True

		self.clientSidePrediction = clientSidePrediction

		#This is how the client corrects itself when a prediction is wrong.
		#0 is simply teleport to the new location, this causes clipping into objects.
		#1 is using segment queries to move as far towards the new direction until you hit another object.
		#This is inaccurate if you hit into an object that can/would be pushed, and due to segment usage, can clip through smaller objects anyway.
		#2 is to resimulate the series of events, using some approximations (attempts to ignore objects that shouldn't have changed.)
		self.resimulationMethod = resimulationMethod

	def connect( self, address, port, message_factory=pygnetic.message.message_factory, **kwargs ):
		self.connection = self._client.connect( address, port, message_factory, **kwargs )
		self.handler = networkhandlers.ClientHandler( self )
		self.connection.add_handler( self.handler )

	def sendInput( self, inputDict ):
		if self.connection.connected:
			self.connection.net_inputEvent( self.networkTick, self.timer, inputDict )

	def createEntities( self, createTuples ):
		for eachTuple in createTuples:
			classDef = self.networkEntsClassDefs[eachTuple[1]+"Network"]
			destGroup = getattr( self.playStateRef(), classDef.playStateGroup )
			inst = classDef( pos=eachTuple[2], vel=eachTuple[3], group=destGroup )
			inst.id = eachTuple[0]

	def removeEntities( self, removeTuples ):
		playState = self.playStateRef()
		for eachId in [ each[0] for each in removeTuples ]:
			eachEnt = self.findEntById( self, eachId )
			if eachEnt is not None:
				eachEnt.removeFromGroup( *eachEnt.groups() )

	def resimulationUsingSweeps( self, eachEnt, deltaPos ):
		#Segment query sweep.
		#This will use four segments, two at the outermost points of the objects (with respect to the direction of travel)
		#And the others goe from the start of one segment to the end of the other, to help avoid clipping through smaller objects.
		#But no promises.

		#Get the starts, I probably need to convert these starts to space co-ords. As the poly one gets the points with respecct to the body location
		if type( eachEnt.shape ) == pymunk.Poly:
			polyPoints = eachEnt.shape.get_points()
			axis = eachEnt.body.velocity.perpendicular()
			start1Proj, start2Proj = pymunk.Vec2d(0,0), pymunk.Vec2d(0,0)
			start1, start2 = None, None
			if eachEnt.body.velocity.y == 0:
				for eachPoint in polyPoints:
					projection = eachPoint.projection( axis )
					if projection.x < 0 and projection.get_length() > start1Proj.get_length():
						start1Proj = projection
						start1 = eachPoint
					elif projection.x > 0 and projection.get_length() > start2Pro.get_length():
						start2Porj = projection
						start2 = eachPoint
			else:
				for eachPoint in polyPoints:
					projection = eachPoint.projection( axis )
					if projection.y < 0 and projection.get_length() > start1Proj.get_length():
						start1Proj = projection
						start1 = eachPoint
					elif projection.y > 0 and projection.get_length() > start2Pro.get_length():
						start2Porj = projection
						start2 = eachPoint
		elif type( eachEnt.Shape ) == pymunk.Circle:
			start1 = eachEnt.body.velocity.perpendicular()*(float(eachEnt.shape.radius)/eachEnt.body.velocity.get_length())
			start2 = eachEnt.body.velocity.perpendicular()*-(float(eachEnt.shape.radius)/eachEnt.body.velocity.get_length())
		else:
			print "Client resimulation doesn't support type: " + eachShape.__class__.__name__

		#So now that I have the starts, make the ends.
		end1 = start1[0] + deltaPos[0], start1[1] + deltaPos[1]
		end2 = start2[0] + deltaPos[0], start2[1] + deltaPos[1]

		#Now create those two diagonal segment sweeps.
		start3, end3 = start1, end2
		start4, end4 = start2, end2

		#SWEEEEEP
		space = self.playStateRef().space

		results = space.segment_query( start1, end1 )
		results.extend( space.segment_query( start2, end2 ) )
		results.extend( space.segment_query( start3, end3 ) )
		results.extend( space.segment_query( start4, end4 ) )

		closestDistance = 10000000
		closestQuery = None
		entPos = eachEnt.getPosition()
		for eachResult in results:
			if eachResult.shape not in eachEnt.physicsObjects and not eachResult.shape.sensor:
				point = eachResult.get_hit_point()
				distance = ( (point[0]-entPos[0])**2 + (point[1]-entPos[1])**2 )**0.5
				if distance < closestDistance:
					closestDistance = distance
					closestQuery = eachResult

		if closestQuery is None:
			#In this scenario, nothing was hit at all, clip the ent by deltaPos.
			eachEnt.setPosition( entPos[0]+deltaPos[0], entPos[1]+deltaPos[1] )
		else:
			point = closestQuery.get_hit_point()
			#Now I need to figure out what side hits this point.

			cRight, cLeft, cBottom, cTop = False, False, False, False
			if type( eachEnt.shape ) == pymunk.Poly or eachEnt.circular:
				if not eachEnt.circular:
					top, bottom, left, right = entPos[1]+eachEnt.wbdy, entPos[1]+eachEnt.wbdy+eachEnt.wbHeight, entPos[0]+eachEnt.wbdx, entPos[0]+eachEnt.wbdx+eachEnt.wbWidth
				else:
					top, bottom, left, right = entPos[1]-eachEnt.radius, entPos[1]+eachENt.radius, entPos[0]-eachEnt.radius, entPos[0]+eachEnt.radius
				if deltaPos[0] == 0:
					if point[1] > top:
						#Clamp the bottom
						cBottom = True
					else:
						#Clamp the top
						cTop = True
				elif deltaPos[1] == 0:
					if point[0] > left:
						#Clamp the right
						cRight = True
					else:
						#Clamp the left
						cLeft = True
				else:
					pTop, pBottom, pRight, pLeft = False, False, False, False
					if point[1] > top:
						#Potentially bottom
						pBottom = True
						if point[0] > left:
							#Potentially right
							pRight = True
							corner = ( right, bottom )
						else:
							#Potentially left
							pLeft = True
							corner = ( left, bottom )
					else:
						#Potentially top
						pTop = True
						if point[0] > left:
							#Potentially right
							pRight = True
							corner = ( right, top )
						else:
							#Potentially left
							pLeft = True
							corner = ( left, top )
					#This messy equation figures out the y of the line extending out from the corner by deltaPos at point x, where x is point[0]
					lineY = (float(deltaPos[1])/deltaPos[0])*(point[0]-corner[0])+corner[1]
	
					if lineY > point[1]:
						#Below the line
						if pBottom:
							#Clamp to bottom
							cBottom = True
						else:
							if pRight:
								#Clamp to right
								cRight = True
							else:
								#Clamp to left
								cLeft = True
					else:
						#Above the line
						if pTop:
							#Clamp to top
							cTop = True
						else:
							if pRight:
								#Clamp to right
								cRight = True
							else:
								#Clamp to left
								cLeft = True
				
				#Now that we know what side to clamp to. FUCKING DO IT ALREADY

				if deltaPos[1] == 0:
					if cLeft:
						newDelta = ( point[0]-(left), 0 )
					else:
						newDelta = ( point[0]-(right), 0 )
				elif deltaPos[0] == 0:
					if cTop:
						newDelta = ( 0, point[1]-(top) )
					else:
						newDelta = ( 0, point[1]-(bottom) )
				else:
					if cTop:
						dy = point[1]-top
						dx = (float(deltaPos[0])/deltaPos[1])*dy
					elif cBottom:
						dy = point[1]-bottom
						dx = (float(deltaPos[0])/deltaPos[1])*dy
					elif cLeft:
						dx = point[0]-left
						dy = (float(deltaPos[1])/deltaPos[1])*dx
					elif cRight:
						dx = point[0]-right
						dy = (float(deltaPos[1])/deltaPos[1])*dx

				newDelta = int(dx), int(dy)

		return newDelta

	def resimulationUsingPymunk( self, time ):
		#So, part of this approximation is that it won't bother remaking everything that was removed from the scene in the mean time, this shouldn't be an issue often however.

		#First, set everything to how it was.
		playState = self.playStateRef()
		for eachSprite in playState.sprites():
			eachSprite.setPosition( eachSprite.logOfPositions[time] )
			eachSprite.velocity.x, eachSprite.velocity.y = eachSprite.logOfVelocities[time]
			eachSprite.force.x, eachSprite.force.y = eachSprite.logOfForces[time]

		#Now, going to resimulate the update steps, 
		

	def findEntById( self, theId ):
		for eachEnt in self.playStateRef().sprites():
			if eachEnt.id == theId:
				return eachEnt
		print "WAT. RECEIVED UPDATE REFERRING TO NON-EXISTANT ENTITY."

	def updatePositions( self, positionTuples, updateTime ):
		playState = self.playStateRef()
		if not self.clientSidePrediction or updateTime is None:
			for eachTuple in positionTuples:
				eachId = eachTuple[0]
				eachEnt = self.findEntById( eachId )
				if eachEnt is None:
					return None
				if eachEnt.collidable:
					eachEnt.body.activate()
				eachEnt.setPosition( eachTuple[1] )
		else:
			for eachTuple in positionTuples:
				eachId = eachTuple[0]
				eachEnt = self.findEntById( eachId )
				if eachEnt is None:
					return None
				if eachEnt.collidable:
					eachEnt.body.activate()
				if eachEnt.logOfPositions.get(updateTime) is not None:
					posAtTime = eachEnt.logOfPositions[updateTime]
					if ( int( posAtTime[0] ), int( posAtTime[1] ) ) != eachTuple[1]:
						deltaPos = eachTuple[1][0]-posAtTime[0], eachTuple[1][1]-posAtTime[1]
						curPos = eachEnt.getPosition()
						newPos = curPos[0]+deltaPos[0], curPos[1]+deltaPos[1]
						#Here I'm going to do the resimulation.
						if self.resimulationMethod is 1 and eachEnt.collidable and newPos!=curPos:
							newDelta = self.resimulationUsingSweeps( eachEnt, deltaPos )
							newPos = curPos[0]+newDelta[0], curPos[1]+newDelta[1]
							if eachEnt.collidable:
								eachEnt.body.activate()
							eachEnt.setPosition( list(newPos) )

							for eachKey, eachVal in eachEnt.logOfPositions.items():
								if eachKey < updateTime:
									del eachEnt.logOfPositions[eachKey]
								else:
									eachEnt.logOfPositions[eachKey] = eachVal[0]+newDelta[0], eachVal[1]+newDelta[1]

						if self.resimulationMethod is 2 and eachEnt.collidable and newPos!=curPos:
							#In the scenario of resimulation method 2 and something had the wrong location,
							resim2Bool = True

						else:
							if eachEnt.collidable:
								eachEnt.body.activate()
							eachEnt.setPosition( list(newPos) )
							for eachKey, eachVal in eachEnt.logOfPositions.items():
								if eachKey < updateTime:
									del eachEnt.logOfPositions[eachKey]
								else:
									eachEnt.logOfPositions[eachKey] = eachVal[0]+deltaPos[0], eachVal[1]+deltaPos[1]
							
					else:
						for eachKey, eachVal in eachEnt.logOfPositions.items():
							if eachKey < updateTime:
								del eachEnt.logOfPositions[eachKey]
				

	def startSounds( self, soundTuples ):
		sndMgr = self.playStateRef().soundManager
		for eachTuple in soundTuples:
			sndMgr.getSound(eachTuple[0]).play( eachTuple[1], eachTuple[2], eachTuple[3], eachTuple[4] )

	def stopSounds( self, soundTuples ):
		sndMgr = self.playStateRef().soundManager
		for eachTuple in soundTuples:
			sndMgr.stopSound( eachTuple[1], eachTuple[0] )

	def swapAnims( self, swapTuples ):
		playState = self.playStateRef()
		for eachTuple in swapTuples:
			eachId = eachTuple[0]
			eachEnt = self.findEntById( eachId )
			if eachEnt is not None:
				eachEnt.swapAnimation( eachTuple[1] )

	def changeAnims( self, changeTuples ):
		playState = self.playStateRef()
		for eachTuple in changeTuples:
			eachId = eachTuple[0]
			eachEnt = self.findEntById( eachId )
			if eachEnt is not None:
				eachEnt.changeAnimation( eachTuple[1] )

	def forceAnims( self, entIdFrameTuples ):
		playState = self.playStateRef()
		for eachTuple in entIdFrameTuples:
			eachId = eachTuple[0]
			eachEnt = self.findEntById( eachId )
			if eacheNt is None:
				return None
			eachEnt.frame = eachTuple[1] - 1
			eachEnt.nextFrame()
			eachEnt.frameTime = eachTuple[2]

	def forcePlayingSounds( self, soundTuples ):
		sndMgr = self.playStateRef().soundManager
		for eachTuple in soundTuples:
			eachSound = sndMgr.getSound( eachTuple[0] )
			playInst = eachSound.play( eachTuple[1], eachTuple[2], eachTuple[3], eachTuple[4], forceNoPlay=True )
			playInst.endTime = sndMgr.curTime+eachTuple[5]
			playInst.attemptRestart( eachSound._pygameSound )

	def forceVelocities( self, entIdVelocityTuples, updateTime ):
		playState = self.playStateRef()
		if not self.clientSidePrediction or updateTime is None:
			for eachTuple in entIdVelocityTuples:
				eachId = eachTuple[0]
				eachEnt = self.findEntById( eachId )
				if eachEnt is None:
					return None
				eachEnt.body.velocity.x = eachTuple[1][0]
				eachEnt.body.velocity.y = eachTuple[1][1]
		else:
			for eachTuple in entIdVelocityTuples:
				eachId = eachTuple[0]
				eachEnt = self.findEntById( eachId )
				velAtTime = eachEnt.logOfVelocities.get(updateTime)
				if velAtTime is not None and velAtTime != eachTuple[1]:
					curPos = eachEnt.getPosition()
					deltaVel = eachTuple[1][0]-velAtTime[0], eachTuple[1][1]-velAtTime[1]
					eachEnt.body.velocity.x = eachEnt.body.velocity.x + deltaVel[0]
					eachEnt.body.velocity.y = eachEnt.body.velocity.y + deltaVel[1]
					deltaPos = deltaVel[0]*(self.timer-updateTime), deltaVel[1]*(self.timer-updateTime)
					if deltaPos[0] > 1 and deltaPos[1] > 1 and self.resimulationMethod is 1 and eachEnt.collidable:
						if eachEnt.collidable:
							eachEnt.body.activate()
						newDelta = self.resimulationUsingSweeps( eachEnt, deltaPos )
						eachEnt.setPosition( ( curPos[0]+newDelta[0], curPos[1]+newDelta[1] ) )
						for eachKey, eachVal in eachEnt.logOfPositions.items():
							if eachKey > updateTime:
								#eachEnt.logOfPositions[eachKey] = eachVal[0]+deltaVel[0]*(eachKey-updateTime), eachVal[1]+deltaVel[1]*(eachKey-updateTime)
								ratio = float(eachKey-updateTime)/(eachkey-self.timer)
								eachEnt.logOfPositions[eachKey] = eachVal[0]+newDelta[0]*ratio, eachVal[1]+newDelta[1]*ratio
						for eachKey, eachVal in eachEnt.logOfVelocities.items():
							if eachKey < updateTime:
								del eachEnt.logOfVelocities[eachKey]
							else:
								eachEnt.logOfVelocities[eachKey] = eachVal[0]+deltaVel[0], eachVal[1]+deltaVel[1]
					else:
						if eachEnt.collidable:
							eachEnt.body.activate()
						eachEnt.setPosition( ( curPos[0]+deltaPos[0], curPos[1]+deltaPos[1] ) )
						for eachKey, eachVal in eachEnt.logOfPositions.items():
							if eachKey > updateTime:
								eachEnt.logOfPositions[eachKey] = eachVal[0]+deltaVel[0]*(eachKey-updateTime), eachVal[1]+deltaVel[1]*(eachKey-updateTime)
						for eachKey, eachVal in eachEnt.logOfVelocities.items():
							if eachKey < updateTime:
								del eachEnt.logOfVelocities[eachKey]
							else:
								eachEnt.logOfVelocities[eachKey] = eachVal[0]+deltaVel[0], eachVal[1]+deltaVel[1]
				else:
					for eachKey, eachVal in eachEnt.logOfVelocities.items():
						if eachKey < updateTime:
							del eachEnt.logOfVelocities[eachKey]
	
	def disconnectAll( self ):
		if self.connection.connected:
			self.connection.disconnect()

	def update( self, dt, timeout=0 ):
		self._client.update( timeout )
		self.timer += dt
