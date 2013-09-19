# Copyright (c) 2013 Connor Sherson
#
# This software is provided 'as-is', without any express or implied
# warranty. In no event will the authors be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
#    1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
#
#    2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
#
#    3. This notice may not be removed or altered from any source
#    distribution.

import extern_modules.pygnetic as pygnetic, networkhandlers, weakref, random, zlib
from collections import namedtuple
from networkupdateclasses import *

#ClientTuple = namedtuple( 'ClientTuple', ['name', 'connection', 'isPlayer', 'time'] )
class ClientInfo:
    def __init__( self, idNum, name, connection, isPlayer, time, lastAckClientTime, lastAckServerTime, readyForUpdates ):
        self.name = name
        self.connection = connection
        self.isPlayer = isPlayer
        self.time = time
        self.lastAckClientTime = lastAckClientTime
        self.lastAckServerTime = lastAckServerTime
        self.inputCount = 0
        self.idNum = idNum
        self.readyForUpdates = readyForUpdates

class NetworkServer:
    def __init__( self, playState, host, port, con_limit=4, networkingMode=0 ):
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
            kwargList = [ ( each, getattr(ent, each) ) for each in ent.importantParams ]
            self.createdEnts.append( CreateEnt( ent.id, ent.__class__.__name__, ent.rect.topleft, vel, dict( kwargList ) ) )
        else:
            kwargList = [ ( each, getattr(ent, each) ) for each in ent.importantParams ]
            return CreateEnt( ent.id, ent.__class__.__name__, ent.rect.topleft, vel, dict( kwargList ) )

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

        self.clients.append( ClientInfo( len(self.clients), info.name, connection, False, info.time, info.time, self.timer, False ) )

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

        #Make the position tuples
        positionTuples = [ UpdatePosition( each.id, each.getPosition() ) for each in playState.sprites() ]
        
        #Make a list of the animations to change them each to, and the forceAnim list.
        changeAnimList = []
        forceAnimList = []
        for each in playState.sprites():
            for eachAnimName, eachAnim in each.animations.items():
                if eachAnim == each.curAnimation:
                    changeAnimList.append( ChangeAnim( each.id, eachAnimName ) )
                    forceAnimList.append( ( each.id, each.frame, each.frameTime ) )
                    break

        #Make a list of the sounds to force midplay.
        forceSoundList  = [ (each.soundFileName, each.priority, each.loops, each.maxtime, each.fade_ms, each.endTime-playState.soundManager.curTime ) for each in playState.soundManager.playInstances ]

        if self.extrapolationOn:
            #Get velocities.
            velocityTuples = [ (each.id, (each.body.velocity.x, each.body.velocity.y)) for each in self.playStateRef().sprites() if each.collidable ]
        else:
            velocityTuples = None

        #Send the update
        client.connection.net_createEvent( self.networkTick, self.timer, None, None, 0, createEntList, [], positionTuples, velocityTuples, [], [], changeAnimList, [] )

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
            self.playStateRef().gameLogicManager.exitGame( client )

    def getPlayerKey( self, client ):
        return client.idNum

    def getClientFromKey( self, key ):
        for eachClient in self.clients:
            if self.getPlayerKey( eachClient ) == key:
                return eachClient
        return None

    def getKeyFromPlayer( self, playerEnt ):
        clientId = None
        for eachId, eachPlayerList in self.players.iteritems():
            if playerEnt in eachPlayerList:
                clientId = eachId
                break
        if clientId is not None:
            return clientId
        return None

    def getClientFromPlayer( self, playerEnt ):
        return self.getClientFromKey( self.getKeyFromPlayer( playerEnt ) )

    def disconnectAll( self ):
        [ each.disconnect() for each in self._server.connections() if each.connected ]

    def updateTime( self, dt ):
        self.timer += dt
        for eachClient in self.clients:
            eachClient.time += dt
        
    def update( self, dt, timeout=0 ):
        self._server.update( timeout )
        
        #Create the network update.
        updatedPositions = [ UpdatePosition( each.id, each.getPosition() ) for each in self.playStateRef().sprites() ]
        createEntUpdates = list( self.createdEnts )
        removeEntUpdates = list( self.removedEnts )
        swapAnimUpdates = list( self.swapAnims )
        changeAnimUpdates = list( self.changeAnims )
        startSoundUpdates = list( self.startSounds )
        stopSoundUpdates = list( self.stopSounds )

        #print self.timer

        if self.extrapolationOn:
            #Create the velocity tuple list.
            velocityTuples = [ (each.id, (each.body.velocity.x, each.body.velocity.y)) for each in self.playStateRef().sprites() if each.collidable ]

        if not self.extrapolationOn:
            #Iterate over every client
            for eachClient in [ each for each in self.clients if each.readyForUpdates ]:
                #Check if the connection is still valid:
                if eachClient.connection.connected:
                    #Time since this client last sent anything:
                    clientDt = self.timer-eachClient.lastAckServerTime
                    #Send each a network update.
                    eachClient.connection.net_updateEvent( self.networkTick, self.timer, eachClient.time+clientDt, eachClient.time, eachClient.inputCount, createEntUpdates, removeEntUpdates, updatedPositions, None, startSoundUpdates, stopSoundUpdates, changeAnimUpdates, swapAnimUpdates )
                    #eachClient.time += dt
                else:
                    #Remove associated players and the client tuple.
                    self.removePlayer( eachClient )
                    self.clients.remove( eachClient )
        else:
            #Iterate over every client
            for eachClient in [ each for each in self.clients if each.readyForUpdates ]:
                #Check if the connection is still valid:
                if eachClient.connection.connected:
                    #print eachClient.time, self.timer
                    #Time since this client last sent anything:
                    clientDt = self.timer-eachClient.lastAckServerTime
                    #Send each a network update.
                    #print eachClient.time, clientDt
                    eachClient.connection.net_updateEvent( self.networkTick, self.timer, eachClient.time+clientDt, eachClient.time, eachClient.inputCount, createEntUpdates, removeEntUpdates, updatedPositions, velocityTuples, startSoundUpdates, stopSoundUpdates, changeAnimUpdates, swapAnimUpdates )
                    #Always force the velocity AFTER an updateEvent
                    #eachClient.connection.net_forceVelocities( self.networkTick, self.timer, eachClient.time, velocityTuples )
                    #eachClient.time += dt
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
        #self.timer += dt
