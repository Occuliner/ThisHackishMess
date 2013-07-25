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

import extern_modules.pygnetic as pygnetic, weakref, os, gzip

from idsource import IdSource
from picklestuff import loadPlayState

class ClientHandler(pygnetic.Handler):
    def __init__( self, client ):
        #The tick that the handler is on, from its own perspective.
        #Set to none by default, and then set it when you recieve your first update from the serv.
        self.networkTick = None

        #A ref to the client itself.
        self.client = weakref.ref( client )

    def net_requestInfo( self, message, **kwargs ):
        playState = self.client().playStateRef()

        playState.gameLogicManager.preNetworkEvent( message )

        if not (message.levelName is "Untitled"):
            #So, if there is a level name, load that level if found.
            newState = loadPlayState( message.levelName, playState.floor.tileSet, self.client().networkEntsClassDefs.values(), networkClient=self.client() )
            if newState is None:
                print "Host was on a level you don't have. Requesting download"
                self.connection.net_requestMapBuffer( self.client().networkTick, message.mapName )
            else:
                playState.swap( newState )
        
        playState.soundManager.idGen = IdSource()
        if message.soundMgrCurPlayId != 0:
            for each in xrange( message.soundMgrCurPlayId+1 ):
                playState.soundManager.idGen.getId()
        playState.soundManager.curPlayId = message.soundMgrCurPlayId

        self.connection.net_hereIsMyInfo( self.client().timer, self.client().name )

        playState.gameLogicManager.postNetworkEvent( message )

    def net_acceptPlayer( self, message, **kwargs ):
        playState = self.client().playStateRef()
        playState.gameLogicManager.preNetworkEvent( message )

        playState.gameLogicManager.postNetworkEvent( message )

    def net_kickPlayer( self, message, **kwargs ):
        playState = self.client().playStateRef()
        playState.gameLogicManager.preNetworkEvent( message )

        playState.gameLogicManager.postNetworkEvent( message )

    def net_chatToClient( self, message, **kwargs ):
        playState = self.client().playStateRef()
        playState.gameLogicManager.preNetworkEvent( message )

        playState.gameLogicManager.postNetworkEvent( message )

    def net_updateEvent( self, message, **kwargs ):
        client = self.client()

        playState = client.playStateRef()
        playState.gameLogicManager.preNetworkEvent( message )

        client.serverTime = message.time

        if "resimulation" in kwargs.keys():
            client.createEntities( message.createEnts )
            client.removeEntities( message.removeEnts )
            return None

        latency = client.timer-message.clientTime

        if client.resimulationMethod == 2:
            if message.clientTime is not None:
                client.resimulationUsingPymunk( message.clientTime, message.clientLastAckTime, latency, message.clientInputCount, message.updatePositions, message.vels )
        else:
            client.updatePositions( message.updatePositions, message.clientTime )
            client.forceVelocities( message.vels, message.clientTime )

        client.createEntities( message.createEnts )
        client.removeEntities( message.removeEnts )
        client.startSounds( message.startSounds )
        client.stopSounds( message.stopSounds )
        client.swapAnims( message.swapAnims )
        client.changeAnims( message.changeAnims )

        client.networkTick = message.tickNum
        
        client.addToMessageLog( message )
        client.addLatencySample( latency )

        playState.gameLogicManager.postNetworkEvent( message )

    def net_createEvent( self, message, **kwargs ):
        client = self.client()
        playState = client.playStateRef()
        playState.gameLogicManager.preNetworkEvent( message )
        client.createEntities( message.createEnts )
        client.removeEntities( message.removeEnts )
        client.startSounds( message.startSounds )
        client.stopSounds( message.stopSounds )
        client.swapAnims( message.swapAnims )
        client.changeAnims( message.changeAnims )
        client.updatePositions( message.updatePositions, message.clientTime )
        client.forceVelocities( message.vels, message.clientTime )

        playState.gameLogicManager.postNetworkEvent( message )

    def net_forceEntFrame( self, message, **kwargs ):
        client = self.client()
        playState = client.playStateRef()
        playState.gameLogicManager.preNetworkEvent( message )
        client.forceAnims( message.entIdFrameTuples )
        playState.gameLogicManager.postNetworkEvent( message )

    def net_hostRequestPing( self, message, **kwargs ):
        playState = self.client().playStateRef()
        playState.gameLogicManager.preNetworkEvent( message )
        self.connection.net_hostRequestPing( message.timeStamp )
        playState.gameLogicManager.postNetworkEvent( message )

    def net_clientRequestPing( self, message, **kwargs ):
        playState = self.client().playStateRef()
        playState.gameLogicManager.preNetworkEvent( message )
        #Here is the ping calc:
        #self.client().timer - message.timeStamp    
        #Find something to do with it.
        pass
        #client = self.client()

        #client.latencySamples.append( message.timeStamp )
        #if ( len( client.latencySamples ) > client.latencySampleSize ):
        #    client.latencySamples.pop(0)
        playState.gameLogicManager.postNetworkEvent( message )

    def net_forcePlayingSound( self, message, **kwargs ):
        playState = self.client().playStateRef()
        playState.gameLogicManager.preNetworkEvent( message )
        self.client().forcePlayingSounds( message.soundTuples )
        playState.gameLogicManager.postNetworkEvent( message )

    def net_setPlayerEnt( self, message, **kwargs ):
        playState = self.client().playStateRef()
        playState.gameLogicManager.preNetworkEvent( message )
        self.client().clientPlayerIds.append( message.id )
        playState.gameLogicManager.postNetworkEvent( message )

    def net_gameLogicCall( self, message, **kwargs ):
        playState = self.client().playStateRef()
        playState.gameLogicManager.callMethod( ( message.methodName, message.callArgs, message.callKwargs ) )

    def net_sendMapBuffer( self, message, **kwargs ):
        destFile = gzip.open( message.mapName, 'wb' )
        destFile.write( message.mapBuffer )
        destFile.close()

    def on_disconnect( self ):
        pass
    
    def on_recive( self, message, **kwargs ):
        print "Unrecognized message: ", message

class ServerHandler(pygnetic.Handler):
    def on_connect( self ):
        playState = self.server.networkServerRef().playStateRef()
        playState.gameLogicManager.preNetworkEvent( None )
        #Check this address isn't in the banlist.
        for eachSet in self.server.networkServerRef().ipBanList:
            if eachSet[0] == self.connection.address:
                self.connection.net_kickPlayer( eachSet[1], eachSet[2] )
                self.connection.disconnect()
                return None
        self.connection.net_requestInfo( playState.soundManager.curPlayId, self.server.networkServerRef().timer, playState.fileName )
        pygnetic.Handler.on_connect( self )
        playState.gameLogicManager.postNetworkEvent( None )

    def net_hereIsMyInfo( self, message, **kwargs ):
        playState = self.server.networkServerRef().playStateRef()
        playState.gameLogicManager.preNetworkEvent( message )
        networkServer = self.server.networkServerRef()
        networkServer.addClient( message, self.connection )

        #Send all the existing state info.
        client = networkServer.getClientByConnection( self.connection )
        networkServer.sendAlreadyExistingState( client )
        playState.gameLogicManager.postNetworkEvent( message )

    def net_joinGame( self, message, **kwargs ):
        playState = self.server.networkServerRef().playStateRef()
        playState.gameLogicManager.preNetworkEvent( message )
        client = self.server.networkServerRef().getClientByConnection( self.connection )
        self.connection.net_acceptPlayer( client.name )
        self.server.networkServerRef().addPlayer( client )
        playState.gameLogicManager.postNetworkEvent( message )

    def net_chatToHost( self, message, **kwargs ):
        playState = self.server.networkServerRef().playStateRef()
        playState.gameLogicManager.preNetworkEvent( message )
        playState.gameLogicManager.postNetworkEvent( message )

    def net_inputEvent( self, message, **kwargs ):
        playState = self.server.networkServerRef().playStateRef()
        networkServer = self.server.networkServerRef()

        playState.gameLogicManager.preNetworkEvent( message )

        client = networkServer.getClientByConnection( self.connection )
        if client is None:
            return None
        client.lastAckClientTime = message.time
        client.time = message.time
        #client.time = max( message.time, client.time )
        client.lastAckServerTime = networkServer.timer
        client.inputCount += 1
        playerKey = networkServer.getPlayerKey( client )
        playerEntList = networkServer.players.get( playerKey, [] )

        for each in playerEntList:
            each.sendInput( message.inputDict )

        playState.gameLogicManager.postNetworkEvent( message )

    def net_clientRequestPing( self, message, **kwargs ):
        playState = self.server.networkServerRef().playStateRef()
        playState.gameLogicManager.preNetworkEvent( message )
        self.connection.net_clientRequestPing( message.timeStamp )
        playState.gameLogicManager.postNetworkEvent( message )

    def net_hostRequestPing( self, message, **kwargs ):
        playState = self.server.networkServerRef().playStateRef()
        playState.gameLogicManager.preNetworkEvent( message )
        #Here is the ping calc:
        #self.server.networkServerRef().timer - message.timeStamp    
        #Find something to do with it.
        playState.gameLogicManager.postNetworkEvent( message )

    def net_playerUpdate( self, message, **kwargs ):
        playState = self.server.networkServerRef().playStateRef()
        networkServer = self.server.networkServerRef()
        client = networkServer.getClientByConnection( self.connection )
        playState.gameLogicManager.preNetworkEvent( message )
        if client is None:
            return None
        playerKey = networkServer.getPlayerKey( client )
        playerEntList = networkServer.players.get( playerKey, [] )

        for eachPlayer in playerEntList:
            if eachPlayer.id == message.id:
                eachPlayer.setPosition( message.loc )
                if eachPlayer.collidable:
                    eachPlayer.body.velocity.x = message.vel[0]
                    eachPlayer.body.velocity.y = message.vel[1]
        playState.gameLogicManager.postNetworkEvent( message )

    def net_requestMapBuffer( self, message, **kwargs ):
        if not os.path.isfile( message.mapName ):
            return None
        theFile = gzip.open( fileName, 'rb' )
        loadString = theFile.read()
        theFile.close()
        self.connection.net_sendMapBuffer( self.server.networkServerRef().networkTick, message.mapName, loadString )

    def on_disconnect( self ):
        self.server.networkServerRef().removeClientByConnection( self.connection )

    def on_recive( self, message, **kwargs ):
        print "Unrecognized message: ", message

