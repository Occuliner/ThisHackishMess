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
	def __init__( self, playState=None, networkEntsClassDefs=None, conn_limit=1, *args, **kwargs ):
		self._server = pygnetic.Client( conn_limit, *args, **kwargs )
		
		self.playStateRef = weakref.ref( playState )

		self.networkTick = None

		self.networkEntsClassDefs = networkEntsClassDefs

	def connect( self, address, port, message_factory=pygnetic.message.message_factory, **kwargs ):
		connection = pygnetic.client.Client.connect( self._server, address, port, message_factory, **kwargs )
		connection.add_handler( networkhandlers.ClientHandler( self ) )

	def createEntities( self, createTuples ):
		for eachTuple in createTuples:
			classDef = self.networkEntsClassDefs[eachTuple.className]
			destGroup = getattr( self.playStateRef(), classDef.playStateGroup )
			inst = classDef( pos=eachTuple.position, vel=eachTuple.velocity, group=destGroup )
			inst.id = eachTuple.entId

	def removeEntities( self, removeTuples ):
		playState = self.playStateRef()
		for eachId in [ each.entId for each in removeTuples ]:
			matchFound = False
			for eachEnt in playState.sprites():
				if eachEnt.id == eachId:
					matchFound = True
					eachEnt.removeFromGroups( eachEnt.groups )
					break
			if not matchFound:		
				print "WAT. RECEIVED UPDATE REFERRING TO NON-EXISTANT ENTITY."

	def updatePositions( self, positionTuples ):
		playState = self.playStateRef()
		for eachTuple in positionTuples:
			eachId = eachTuple.entId
			matchFound = False
			for eachEnt in playState.sprites():
				if eachEnt.id == eachId:
					matchFound = True
					eachEnt.setPosition( eachTuple.newPosition )
			if not matchFound:
				print "WAT. RECEIVED UPDATE REFERRING TO NON-EXISTANT ENTITY."

	def startSounds( self, soundTuples ):
		sndMgr = self.playStateRef().soundManager
		for eachTuple in soundTuples:
			sndMgr.getSound(eachTuple.soundName).play( eachTuple.priority, eachTuple.loops, eachTuple.maxtime, eachTuple.fade_ms )

	def stopSounds( self, soundTuples ):
		sndMgr = self.playStateRef().soundManager
		for eachTuple in soundTuples:
			sndMgr.stopSound( eachTuple.soundName, eachTuple.stopId )

	def swapAnims( self, swapTuples ):
		playState = self.playStateRef()
		for eachTuple in swapTuples:
			eachId = eachTuple.entId
			matchFound = False
			for eachEnt in playState.sprites():
				if eachEnt.id == eachId:
					matchFound = True
					eachEnt.swapAnimation( eachTuple.newAnimName )
			if not matchFound:
				print "WAT. RECEIVED UPDATE REFERRING TO NON-EXISTANT ENTITY."

	def changeAnims( self, changeTuples ):
		playState = self.playStateRef()
		for eachTuple in changeTuples:
			eachId = eachTuple.entId
			matchFound = False
			for eachEnt in playState.sprites():
				if eachEnt.id == eachId:
					matchFound = True
					eachEnt.changeAnimation( eachTuple.newAnimName )
			if not matchFound:
				print "WAT. RECEIVED UPDATE REFERRING TO NON-EXISTANT ENTITY."
