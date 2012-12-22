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

import extern_modules.pygnetic as pygnetic, networkhandlers, weakref

class NetworkClient:
	def __init__( self, playState=None, networkEntsClassDefs=None, conn_limit=1, networkingMode=0, clientSidePrediction=True, *args, **kwargs ):
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
			matchFound = False
			for eachEnt in playState.sprites():
				if eachEnt.id == eachId:
					matchFound = True
					eachEnt.removeFromGroup( *eachEnt.groups() )
					break
			if not matchFound:		
				print "WAT. RECEIVED UPDATE REFERRING TO NON-EXISTANT ENTITY."

	def updatePositions( self, positionTuples, updateTime ):
		playState = self.playStateRef()
		if not self.clientSidePrediction or updateTime is None:
			for eachTuple in positionTuples:
				eachId = eachTuple[0]
				matchFound = False
				for eachEnt in playState.sprites():
					if eachEnt.id == eachId:
						matchFound = True
						eachEnt.setPosition( eachTuple[1] )
						break
				if not matchFound:
					print "WAT. RECEIVED UPDATE REFERRING TO NON-EXISTANT ENTITY."
		else:
			for eachTuple in positionTuples:
				eachId = eachTuple[0]
				matchFound = False
				for eachEnt in playState.sprites():
					if eachEnt.id == eachId:
						matchFound = True
						if eachEnt.logOfPositions.get(updateTime) is not None:
							posAtTime = eachEnt.logOfPositions[updateTime]
							deltaPos = eachTuple[1][0]-posAtTime[0], eachTuple[1][1]-posAtTime[1]
							curPos = eachEnt.getPosition()
							newPos = curPos[0]+deltaPos[0], curPos[1]+deltaPos[1]
							if self.extrapolationOn and eachEnt.collidable:
								velAtTime = eachEnt.logOfVelocities[updateTime]
								newPos = newPos[0]-velAtTime[0]*(self.timer-updateTime), newPos[1]-velAtTime[1]*(self.timer-updateTime)
								eachEnt.setPosition( list(newPos) )
								for eachKey, eachVal in eachEnt.logOfPositions.items():
									if eachKey < updateTime:
										del eachEnt.logOfPositions[eachKey]
									else:
										eachEnt.logOfPositions[eachKey] = eachVal[0]+deltaPos[0]-velAtTime[0]*(eachKey-updateTime), eachVal[1]+deltaPos[1]-velAtTime[1]*(eachKey-updateTime)
							else:
								eachEnt.setPosition( list(newPos) )
								for eachKey, eachVal in eachEnt.logOfPositions.items():
									if eachKey < updateTime:
										del eachEnt.logOfPositions[eachKey]
									else:
										eachEnt.logOfPositions[eachKey] = eachVal[0]+deltaPos[0], eachVal[1]+deltaPos[1]
						#eachEnt.setPosition( eachTuple[1] )
						break
				if not matchFound:
					print "WAT. RECEIVED UPDATE REFERRING TO NON-EXISTANT ENTITY."

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
			matchFound = False
			for eachEnt in playState.sprites():
				if eachEnt.id == eachId:
					matchFound = True
					eachEnt.swapAnimation( eachTuple[1] )
					break
			if not matchFound:
				print "WAT. RECEIVED UPDATE REFERRING TO NON-EXISTANT ENTITY."

	def changeAnims( self, changeTuples ):
		playState = self.playStateRef()
		for eachTuple in changeTuples:
			eachId = eachTuple[0]
			matchFound = False
			for eachEnt in playState.sprites():
				if eachEnt.id == eachId:
					matchFound = True
					eachEnt.changeAnimation( eachTuple[1] )
					break
			if not matchFound:
				print "WAT. RECEIVED UPDATE REFERRING TO NON-EXISTANT ENTITY."

	def forceAnims( self, entIdFrameTuples ):
		playState = self.playStateRef()
		for eachTuple in entIdFrameTuples:
			eachId = eachTuple[0]
			matchFound = False
			for eachEnt in playState.sprites():
				if eachEnt.id == eachId:
					matchFound = True
					eachEnt.frame = eachTuple[1] - 1
					eachEnt.nextFrame()
					eachEnt.frameTime = eachTuple[2]
					break
			if not matchFound:
				print "WAT. RECEIVED UPDATE REFERRING TO NON-EXISTANT ENTITY."

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
				matchFound = False
				for eachEnt in playState.sprites():
					if eachEnt.id == eachId:
						matchFound = True
						eachEnt.body.velocity.x = eachTuple[1][0]
						eachEnt.body.velocity.y = eachTuple[1][1]
						break
				if not matchFound:
					print "WAT. RECEIVED UPDATE REFERRING TO NON-EXISTANT ENTITY."
		else:
			for eachTuple in entIdVelocityTuples:
				eachId = eachTuple[0]
				matchFound = False
				for eachEnt in playState.sprites():
					if eachEnt.id == eachId:
						matchFound = True
						if eachEnt.logOfVelocities.get(updateTime) is not None:
							curPos = eachEnt.getPosition()
							deltaPos = eachTuple[1][0]*(self.timer-updateTime), eachTuple[1][1]*(self.timer-updateTime)
							eachEnt.setPosition( ( curPos[0]+deltaPos[0], curPos[1]+deltaPos[1] ) )
							velAtTime = eachEnt.logOfVelocities[updateTime]
							deltaVel = eachTuple[1][0]-velAtTime[0], eachTuple[1][1]-velAtTime[1]
							eachEnt.body.velocity.x = eachEnt.body.velocity.x + deltaVel[0]
							eachEnt.body.velocity.y = eachEnt.body.velocity.y + deltaVel[1]
							for eachKey, eachVal in eachEnt.logOfPositions.items():
								if eachKey > updateTime:
									eachEnt.logOfPositions[eachKey] = eachVal[0]+eachTuple[1][0]*(eachKey-updateTime), eachVal[1]+eachTuple[1][1]*(eachKey-updateTime)
							for eachKey, eachVal in eachEnt.logOfVelocities.items():
								if eachKey < updateTime:
									del eachEnt.logOfVelocities[eachKey]
								else:
									eachEnt.logOfVelocities[eachKey] = eachVal[0]+deltaVel[0], eachVal[1]+deltaVel[1]
						break
				if not matchFound:
					print "WAT. RECEIVED UPDATE REFERRING TO NON-EXISTANT ENTITY."
	
	def disconnectAll( self ):
		if self.connection.connected:
			self.connection.disconnect()

	def update( self, dt, timeout=0 ):
		self._client.update( timeout )
		self.timer += dt
