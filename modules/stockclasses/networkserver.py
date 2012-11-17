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

import extern_modules.pygnetic as pygnetic, networkhandlers, weakref, random, zlib
from collections import namedtuple
from networkupdateclasses import *

ClientTuple = namedtuple( 'ClientTuple', ['name', 'connection', 'isPlayer'] )

class NetworkServer( pygnetic.Server ):
	def __init__( self, playState, host="", port=0, con_limit=4, *args, **kwargs ):
		pygnetic.Server.__init__( self, host, port, con_limit, *args, **kwargs )
		self.handler = networkhandlers.ServerHandler

		#The tick that the server is on, from its own perspective.
		self.networkTick = 0

		self.playStateRef = weakref.ref(playState)

		#List of addresses to auto-kick then disconnect. Should pull this from a file.
		#It should be a tuple of 3 things, the address, the duration, the reason.
		self.ipBanList = []

		self.clients = []

		self.createdEnts = []
		self.removedEnts = []

		#This is a dictionary of entities that different clients have permission to send inputDicts to.
		#The key is the md5 sum created from throwing the md5StartString and the client name into md5.
		self.players = {}

	def addClient( self, info, connection ):
		#First, checck to see if there's still a connection to the address.
		if not ( connection.address in [each.address for each in self.connections()] ):
			return None

		self.clients.append( ClientTuple( info.name, connection, False ) )
	
	def getClientByConnection( self, connection ):
		for eachClient in self.clients:
			if eachClient.connection == connection:
				return eachClient

	def removeClientByConnection( self, connection ):
		client = self.getClientByConnection( connection )
		if client is not None:
			self.clients.remove( client )
			if client.isPlayer:
				self.removePlayer( client )

	def getPlayerKey( self, client ):
		"""Return the adler32 digest of the client name"""
		return zlib.alder32( client.name )

	def addPlayer( self, client ):
		#This can vary HUGELY. So it will do nothing by default.
		#The idea is that you should probably create a player instance here.
		#Below is a template for this method
		
		#if not client.isPlayer:
		#	playerEntity = CREATIONHERE
		#	self.players[self.getPlayerKey( client )] = [ playerEntity ]
		#	client.isPlayer = True
		pass

	def removePlayer( self, client ):
		#Again, this can vary a lot, so by default it does nothing.

		#But what you want is probably something like this:
		#playerKey = self.getPlayerKey( client )
		#playerEntList = self.players[playerKey]
		#del self.players[playerKey]
		#for each in playerEntList:
		#	each.kill()
		pass

	def update( self, timeout=0 ):
		pygnetic.Sever.update( self, timeout )
		
		#Create the network update.
		updatedPositions = [ UpdatedPosition( each.id, each.rect.topleft ) for each in self.playStateRef() ]
		createEntUpdates = [ CreateEnt( each[0], each[1], each[2] )for each in self.createdEnts ]
		removeEntUpdates = [ RemoveEnt( each ) for each in self.removedEnts ]

		#Iterate over every client
		for eachClient in self.clients:
			#Send each a network update.
			eachClient.connection.net_updateEvent( self.networkTick, createEntUpdates, removeEntUpdates, updatePositions, [], [], [], [] )

		#Clear for the next update
		self.createdEnts = []
		self.removedEnts = []
