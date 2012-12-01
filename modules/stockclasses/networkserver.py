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

class NetworkServer:
	def __init__( self, playState=None, host="", port=1337, con_limit=4, networkingMode=0 ):
		self._server = pygnetic.Server( host, port, con_limit )
		self._server.handler = networkhandlers.ServerHandler
		self._server.networkServerRef = weakref.ref( self )

		#The tick that the server is on, from its own perspective.
		self.networkTick = 0

		self.playStateRef = weakref.ref(playState)

		#List of addresses to auto-kick then disconnect. Should pull this from a file.
		#It should be a tuple of 3 things, the address, the duration, the reason.
		self.ipBanList = []

		self.clients = []

		self.createdEnts = []
		self.removedEnts = []
		self.swapAnims = []
		self.changeAnims = []
		self.startSounds = []
		self.stopSounds = []

		#This is a dictionary of entities that different clients have permission to send inputDicts to.
		#The key is the md5 sum created from throwing the md5StartString and the client name into md5.
		self.players = {}

		self.timer = 0.0

		#Networking mode is whether the client will merely recreate the state as sent from the host, and send input, or use interpolation and/or extrapolation.
		#0=No interoplation/extrapoltion, 1=Extrapolation, 2=Interpolation.
		self.interpolationOn, self.extrapolationOn = False, False
		if networkingMode is 1:
			self.extrapolationOn = True
		elif networkingMode is 2:
			self.interpolationOn = True

	def addCreateEnt( self, ent, forceReturn=False ):
		if ent.collidable:
			vel = [ent.body.velocity[0], ent.body.velocity[1]]
		else:
			vel = [0.0,0.0]
		#self.createdEnts.append( CreateEnt( ent.id, ent.__class__.__name__, ent.getPosition(), vel ) )
		if not forceReturn:
			self.createdEnts.append( CreateEnt( ent.id, ent.__class__.__name__, ent.rect.topleft, vel ) )
		else:
			return CreateEnt( ent.id, ent.__class__.__name__, ent.rect.topleft, vel )

	def addRemoveEnt( self, ent ):
		self.removedEnts.append( RemoveEnt( ent.id ) )

	def addSwapAnim( self, ent, animName ):
		self.swapAnims.append( SwapAnim( ent.id, animName ) )

	def addChangeAnim( self, ent, animName ):
		self.changeAnims.append( ChangeAnim( ent.id, animName ) )

	def addStartSound( self, soundName, priority, loops, maxtime, fade_ms ):
		self.startSounds.append( StartSound( soundName, priority, loops, maxtime, fade_ms ) )

	def addStopSound( self, soundName, stopId ):
		self.stopSounds.append( StopSound( stopId, soundName ) )

	def addClient( self, info, connection ):
		#First, checck to see if there's still a connection to the address.
		if not ( connection.address in [each.address for each in self._server.connections()] ):
			return None

		self.clients.append( ClientTuple( info.name, connection, False ) )

	def sendAlreadyExistingState( self, client ):
		playState = self.playStateRef()

		#Get the list of entities we need info on.
		entNum = playState.amountOfEntsOnLoad
		if entNum is None:
			listOfEntsToSend = playState.sprites()
		else:
			listOfEntsToSend = [ each for each in playState.sprites() if each.id >= entNum ]

		#Make a create list
		createEntList = [ self.addCreateEnt( each, forceReturn=True ) for each in listOfEntsToSend ]
		
		#Make a list of the animations to change them each to, and the forceAnim list.
		changeAnimList = []
		forceAnimList = []
		for each in listOfEntsToSend:
			for eachAnimName, eachAnim in each.animations.items():
				if eachAnim == each.curAnimation:
					changeAnimList.append( ChangeAnim( each.id, eachAnimName ) )
					forceAnimList.append( ( each.id, each.frame, each.frameTime ) )
					break

		#Make a list of the sounds to force midplay.
		forceSoundList  = [ (each.soundFileName, each.priority, each.loops, each.maxtime, each.fade_ms, each.endTime-playState.soundManager.curTime ) for each in playState.soundManager.playInstances ]

		#Send the update
		client.connection.net_updateEvent( self.networkTick, createEntList, [], [], [], [], changeAnimList, [] )

		#Now send the forceAnims.
		client.connection.net_forceEntFrame( self.networkTick, forceAnimList )

		#Now send the forceSounds.
		client.connection.net_forcePlayingSound( self.networkTick, forceSoundList )

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
		if client is not None:
			return zlib.adler32( client.name )

	def addPlayer( self, client ):
		#This can vary HUGELY.
		#The idea is that you should probably create a player instance here.
		#Below is a template for this method
		
		if not client.isPlayer:
			for each in self.playStateRef().devMenuRef().masterEntSet.individualSets["players"]:
				if each.__name__ == "YasbClass":
					classDef = each
					break
			destGroup = getattr( self.playStateRef(), "networkPlayers" )
			playerEntity = classDef( pos=[0,0], vel=[0,0], group=destGroup )
			self.players[self.getPlayerKey( client )] = [ playerEntity ]
			self.clients.remove( client )
			self.clients.append( ClientTuple( client.name, client.connection, True ) )

	def removePlayer( self, client ):
		#Again, this can vary a lot.
		#But what you want is probably something like this:
		if client.isPlayer:
			playerKey = self.getPlayerKey( client )
			playerEntList = self.players[playerKey]
			del self.players[playerKey]
			for each in playerEntList:
				each.kill()

	def disconnectAll( self ):
		[ each.disconnect() for each in self._server.connections() if each.connected ]

	def update( self, dt, timeout=0 ):
		self._server.update( timeout )
		
		#Create the network update.
		updatedPositions = [ UpdatePosition( each.id, each.rect.topleft ) for each in self.playStateRef().sprites() ]
		createEntUpdates = list( self.createdEnts )
		removeEntUpdates = list( self.removedEnts )
		swapAnimUpdates = list( self.swapAnims )
		changeAnimUpdates = list( self.changeAnims )
		startSoundUpdates = list( self.startSounds )
		stopSoundUpdates = list( self.stopSounds )

		if self.extrapolationOn:
			#Create the velocity tuple list.
			velocityTuples = [ (each.id, (each.body.velocity.x, each.body.velocity.y)) for each in self.playStateRef().sprites() if each.collidable ]

		if not self.extrapolationOn:
			#Iterate over every client
			for eachClient in self.clients[:]:
				#Check if the connection is still valid:
				if eachClient.connection.connected:
					#Send each a network update.
					eachClient.connection.net_updateEvent( self.networkTick, createEntUpdates, removeEntUpdates, updatedPositions, startSoundUpdates, stopSoundUpdates, changeAnimUpdates, swapAnimUpdates )
				else:
					#Remove associated players and the client tuple.
					self.removePlayer( eachClient )
					self.clients.remove( eachClient )
		else:
			#Iterate over every client
			for eachClient in self.clients[:]:
				#Check if the connection is still valid:
				if eachClient.connection.connected:
					#Send each a network update.
					eachClient.connection.net_updateEvent( self.networkTick, createEntUpdates, removeEntUpdates, updatedPositions, startSoundUpdates, stopSoundUpdates, changeAnimUpdates, swapAnimUpdates )
					eachClient.connection.net_forceVelocities( self.networkTick, velocityTuples )
				else:
					#Remove associated players and the client tuple.
					self.removePlayer( eachClient )
					self.clients.remove( eachClient )

		#Clear for the next update
		self.createdEnts = []
		self.removedEnts = []
		self.swapAnims = []
		self.changeAnims = []
		self.startSounds = []
		self.stopSounds = []

		self.networkTick += 1
		self.timer += dt
