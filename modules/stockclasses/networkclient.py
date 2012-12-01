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
	def __init__( self, playState=None, networkEntsClassDefs=None, conn_limit=1, networkingMode=0 *args, **kwargs ):
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

	def connect( self, address, port, message_factory=pygnetic.message.message_factory, **kwargs ):
		self.connection = self._client.connect( address, port, message_factory, **kwargs )
		self.handler = networkhandlers.ClientHandler( self )
		self.connection.add_handler( self.handler )

	def sendInput( self, inputDict ):
		if self.connection.connected and len(inputDict) > 0:
			self.connection.net_inputEvent( self.networkTick, inputDict )

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

	def updatePositions( self, positionTuples ):
		playState = self.playStateRef()
		for eachTuple in positionTuples:
			eachId = eachTuple[0]
			matchFound = False
			for eachEnt in playState.sprites():
				if eachEnt.id == eachId:
					matchFound = True
					eachEnt.setPosition( eachTuple[1] )
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
			if not matchFound:
				print "WAT. RECEIVED UPDATE REFERRING TO NON-EXISTANT ENTITY."

	def forcePlayingSounds( self, soundTuples ):
		sndMgr = self.playStateRef().soundManager
		for eachTuple in soundTuples:
			eachSound = sndMgr.getSound( eachTuple[0] )
			playInst = eachSound.play( eachTuple[1], eachTuple[2], eachTuple[3], eachTuple[4], forceNoPlay=True )
			playInst.endTime = sndMgr.curTime+eachTuple[5]
			playInst.attemptRestart( eachSound._pygameSound )

	def disconnectAll( self ):
		if self.connection.connected:
			self.connection.disconnect()

	def update( self, dt, timeout=0 ):
		self._client.update( timeout )
		self.timer += dt
