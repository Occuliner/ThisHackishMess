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

import extern_modules.pygnetic as pygnetic, networkmessages, weakref

from idsource import IdSource

class ClientHandler(pygnetic.Handler):
	def __init__( self, client ):
		#The tick that the handler is on, from its own perspective.
		#Set to none by default, and then set it when you recieve your first update from the serv.
		self.networkTick = None

		#A ref to the client itself.
		self.client = weakref.ref( client )

	def net_requestInfo( self, message, **kwargs ):
		playState = self.client().playStateRef()
		playState.soundManager.idGen = IdSource()
		if message.soundMgrCurPlayId != 0:
			for each in xrange( message.soundMgrCurPlayId+1 ):
				playState.soundManager.idGen.getId()
		playState.soundManager.curPlayId = message.soundMgrCurPlayId
		
		self.connection.net_hereIsMyInfo( self.client().name )

	def net_acceptPlayer( self, message, **kwargs ):
		pass
	def net_kickPlayer( self, message, **kwargs ):
		pass
	def net_chatToClient( self, message, **kwargs ):
		pass
	def net_updateEvent( self, message, **kwargs ):
		client = self.client()

		client.createEntities( message.createEnts )
		client.removeEntities( message.removeEnts )
		client.updatePositions( message.updatePositions )
		client.startSounds( message.startSounds )
		client.stopSounds( message.stopSounds )
		client.swapAnims( message.swapAnims )
		client.changeAnims( message.changeAnims )

		client.networkTick = message.tickNum
	def on_disconnect( self ):
		pass
	
	def on_revice( self, message, **kwargs ):
		print "Unrecognized message: ", message

class ServerHandler(pygnetic.Handler):
	def on_connect( self ):
		#Check this address isn't in the banlist.
		for eachSet in self.server.networkServerRef().ipBanList:
			if eachSet[0] == self.connection.address:
				self.connection.kick_player( eachSet[1], eachSet[2] )
				self.connection.disconnect()
				return None
		playState = self.server.networkServerRef().playStateRef()
		self.connection.net_requestInfo( playState.soundManager.curPlayId )
		pygnetic.Handler.on_connect( self )

	def net_hereIsMyInfo( self, message, **kwargs ):
		self.server.networkServerRef().addClient( message, self.connection )

	def net_joinGame( self, message, **kwargs ):
		client = self.server.networkServerRef().getClientByConnection( self.connection )
		self.connection.net_acceptPlayer( client.name )
		self.server.networkServerRef().addPlayer( client )

	def net_chatToHost( self, message, **kwargs ):
		pass

	def net_inputEvent( self, message, **kwargs ):
		client = self.server.networkServerRef().getClientByConnection( self.connection )
		
		playerKey = self.server.networkServerRef().getPlayerKey( client )
		playerEntList = self.server.networkServerRef().players.get( playerKey, [] )

		for each in playerEntList:
			each.sendInput( message.inputDict )

	def on_disconnect( self ):
		self.server.networkServerRef().removeClientByConnection( self.connection )

	def on_revice( self, message, **kwargs ):
		print "Unrecognized message: ", message

