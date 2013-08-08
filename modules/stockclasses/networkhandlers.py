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

import extern_modules.pygnetic as pygnetic, weakref, os, gzip, zlib

class ClientHandler(pygnetic.Handler):
    def __init__( self, client ):
        #The tick that the handler is on, from its own perspective.
        #Set to none by default, and then set it when you recieve your first update from the serv.
        self.networkTick = None

        #A ref to the client itself.
        self.client = weakref.ref( client )

    def net_requestInfo( self, message, **kwargs ):
        playState = self.client().playStateRef()

        playState.gameLogicManager.preNetworkEvent( message, self.connection )

        self.connection.net_hereIsMyInfo( self.client().timer, self.client().name )

        playState.gameLogicManager.postNetworkEvent( message, self.connection )

    def net_loadMap( self, message, **kwargs ):
        playState = self.client().playStateRef()

        playState.gameLogicManager.preNetworkEvent( message, self.connection )

        self.client().loadMap( message.levelName, message.soundMgrCurPlayId )

        self.client().clientPlayerIds = []

        playState.gameLogicManager.postNetworkEvent( message, self.connection )

    def net_acceptPlayer( self, message, **kwargs ):
        playState = self.client().playStateRef()
        playState.gameLogicManager.preNetworkEvent( message, self.connection )

        playState.gameLogicManager.postNetworkEvent( message, self.connection )

    def net_kickPlayer( self, message, **kwargs ):
        playState = self.client().playStateRef()
        playState.gameLogicManager.preNetworkEvent( message, self.connection )

        playState.gameLogicManager.postNetworkEvent( message, self.connection )

    def net_chatToClient( self, message, **kwargs ):
        playState = self.client().playStateRef()
        playState.gameLogicManager.preNetworkEvent( message, self.connection )

        playState.gameLogicManager.postNetworkEvent( message, self.connection )

    def net_updateEvent( self, message, **kwargs ):
        client = self.client()

        playState = client.playStateRef()
        playState.gameLogicManager.preNetworkEvent( message, self.connection )

        client.serverTime = message.time

        latency = client.timer-message.clientTime

        client.createEntities( message.createEnts )
        if client.resimulationMethod == 2:
            if message.clientTime is not None:
                client.resimulationUsingPymunk( message.clientTime, message.clientLastAckTime, latency, message.clientInputCount, message.updatePositions, message.vels )
        else:
            client.updatePositions( message.updatePositions, message.clientTime )
            client.forceVelocities( message.vels, message.clientTime )
        client.removeEntities( message.removeEnts )
        client.startSounds( message.startSounds )
        client.stopSounds( message.stopSounds )
        client.swapAnims( message.swapAnims )
        client.changeAnims( message.changeAnims )

        client.networkTick = message.tickNum
        
        client.addToMessageLog( message )
        client.addLatencySample( latency )

        playState.gameLogicManager.postNetworkEvent( message, self.connection )

    def net_createEvent( self, message, **kwargs ):
        client = self.client()
        playState = client.playStateRef()
        playState.gameLogicManager.preNetworkEvent( message, self.connection )
        client.createEntities( message.createEnts )
        client.removeEntities( message.removeEnts )
        client.startSounds( message.startSounds )
        client.stopSounds( message.stopSounds )
        client.swapAnims( message.swapAnims )
        client.changeAnims( message.changeAnims )
        client.updatePositions( message.updatePositions, message.clientTime )
        client.forceVelocities( message.vels, message.clientTime )

        self.connection.net_everythingIsSet( client.networkTick )

        playState.gameLogicManager.postNetworkEvent( message, self.connection )

    def net_forceEntFrame( self, message, **kwargs ):
        client = self.client()
        playState = client.playStateRef()
        playState.gameLogicManager.preNetworkEvent( message, self.connection )
        client.forceAnims( message.entIdFrameTuples )
        playState.gameLogicManager.postNetworkEvent( message, self.connection )

    def net_hostRequestPing( self, message, **kwargs ):
        playState = self.client().playStateRef()
        playState.gameLogicManager.preNetworkEvent( message, self.connection )
        self.connection.net_hostRequestPing( message.timeStamp )
        playState.gameLogicManager.postNetworkEvent( message, self.connection )

    def net_clientRequestPing( self, message, **kwargs ):
        playState = self.client().playStateRef()
        playState.gameLogicManager.preNetworkEvent( message, self.connection )
        #Here is the ping calc:
        #self.client().timer - message.timeStamp    
        #Find something to do with it.
        pass
        #client = self.client()

        #client.latencySamples.append( message.timeStamp )
        #if ( len( client.latencySamples ) > client.latencySampleSize ):
        #    client.latencySamples.pop(0)
        playState.gameLogicManager.postNetworkEvent( message, self.connection )

    def net_forcePlayingSound( self, message, **kwargs ):
        playState = self.client().playStateRef()
        playState.gameLogicManager.preNetworkEvent( message, self.connection )
        self.client().forcePlayingSounds( message.soundTuples )
        playState.gameLogicManager.postNetworkEvent( message, self.connection )

    def net_setPlayerEnt( self, message, **kwargs ):
        playState = self.client().playStateRef()
        playState.gameLogicManager.preNetworkEvent( message, self.connection )
        self.client().clientPlayerIds.append( message.id )
        playState.gameLogicManager.postNetworkEvent( message, self.connection )

    def net_gameLogicCall( self, message, **kwargs ):
        playState = self.client().playStateRef()
        playState.gameLogicManager.callMethod( ( message.methodName, message.callArgs, message.callKwargs ) )

    def net_sendMapBuffer( self, message, **kwargs ):
        playState = self.client().playStateRef()
        playState.gameLogicManager.preNetworkEvent( message, self.connection )
        destFile = gzip.open( message.mapName, 'wb' )
        destFile.write( zlib.decompress( message.mapBuffer ) )
        destFile.close()
        #Request loadmap.
        self.connection.net_requestLoadMap( self.client().networkTick )
        playState.gameLogicManager.postNetworkEvent( message, self.connection )

    def on_disconnect( self ):
        pass
    
    def on_recive( self, message, **kwargs ):
        print "Unrecognized message: ", message

class ServerHandler(pygnetic.Handler):
    def on_connect( self ):
        playState = self.server.networkServerRef().playStateRef()
        playState.gameLogicManager.preNetworkEvent( None, self.connection )
        #Check this address isn't in the banlist.
        for eachSet in self.server.networkServerRef().ipBanList:
            if eachSet[0] == self.connection.address:
                self.connection.net_kickPlayer( eachSet[1], eachSet[2] )
                self.connection.disconnect()
                return None
        self.connection.net_requestInfo( self.server.networkServerRef().timer )
        self.connection.net_loadMap( self.server.networkServerRef().networkTick, playState.fileName, playState.soundManager.curPlayId )
        pygnetic.Handler.on_connect( self )
        playState.gameLogicManager.postNetworkEvent( None, self.connection )

    def net_hereIsMyInfo( self, message, **kwargs ):
        playState = self.server.networkServerRef().playStateRef()
        playState.gameLogicManager.preNetworkEvent( message, self.connection )
        networkServer = self.server.networkServerRef()
        networkServer.addClient( message, self.connection )

        playState.gameLogicManager.postNetworkEvent( message, self.connection )

    def net_requestState( self, message, **kwargs ):
        #Send all the existing state info.
        playState = self.server.networkServerRef().playStateRef()
        playState.gameLogicManager.preNetworkEvent( message, self.connection )
        networkServer = self.server.networkServerRef()
        client = networkServer.getClientByConnection( self.connection )

        networkServer.sendAlreadyExistingState( client )

        playState.gameLogicManager.postNetworkEvent( message, self.connection )

    def net_joinGame( self, message, **kwargs ):
        playState = self.server.networkServerRef().playStateRef()
        playState.gameLogicManager.preNetworkEvent( message, self.connection )
        client = self.server.networkServerRef().getClientByConnection( self.connection )
        self.connection.net_acceptPlayer( client.name )
        
        playState.gameLogicManager.joinGame( client )

        playState.gameLogicManager.postNetworkEvent( message, self.connection )

    def net_chatToHost( self, message, **kwargs ):
        playState = self.server.networkServerRef().playStateRef()
        playState.gameLogicManager.preNetworkEvent( message, self.connection )
        playState.gameLogicManager.postNetworkEvent( message, self.connection )

    def net_inputEvent( self, message, **kwargs ):
        playState = self.server.networkServerRef().playStateRef()
        networkServer = self.server.networkServerRef()

        playState.gameLogicManager.preNetworkEvent( message, self.connection )

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

        playState.gameLogicManager.postNetworkEvent( message, self.connection )

    def net_clientRequestPing( self, message, **kwargs ):
        playState = self.server.networkServerRef().playStateRef()
        playState.gameLogicManager.preNetworkEvent( message, self.connection )
        self.connection.net_clientRequestPing( message.timeStamp )
        playState.gameLogicManager.postNetworkEvent( message, self.connection )

    def net_hostRequestPing( self, message, **kwargs ):
        playState = self.server.networkServerRef().playStateRef()
        playState.gameLogicManager.preNetworkEvent( message, self.connection )
        #Here is the ping calc:
        #self.server.networkServerRef().timer - message.timeStamp    
        #Find something to do with it.
        playState.gameLogicManager.postNetworkEvent( message, self.connection )

    def net_playerUpdate( self, message, **kwargs ):
        playState = self.server.networkServerRef().playStateRef()
        networkServer = self.server.networkServerRef()
        client = networkServer.getClientByConnection( self.connection )
        playState.gameLogicManager.preNetworkEvent( message, self.connection )
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
        playState.gameLogicManager.postNetworkEvent( message, self.connection )

    def net_requestMapBuffer( self, message, **kwargs ):
        playState = self.server.networkServerRef().playStateRef()
        playState.gameLogicManager.preNetworkEvent( message, self.connection )
        if not os.path.isfile( message.mapName ):
            return None
        theFile = gzip.open( fileName, 'rb' )
        loadString = theFile.read()
        theFile.close()
        self.connection.net_sendMapBuffer( self.server.networkServerRef().networkTick, message.mapName, zlib.compress( loadString ) )
        playState.gameLogicManager.postNetworkEvent( message, self.connection )

    def net_playerIsDead( self, message, **kwargs ):
        networkServer = self.server.networkServerRef()
        playState = networkServer.playStateRef()
        playState.gameLogicManager.preNetworkEvent( message, self.connection )
        client = networkServer.getClientByConnection( self.connection )

        if client is not None:
            playerKey = networkServer.getPlayerKey( client )
            playerEntList = networkServer.players.get( playerKey, [] )

            for eachPlayer in playerEntList:
                if eachPlayer.id == message.entId:
                    eachPlayer.kill()
                    break

        playState.gameLogicManager.postNetworkEvent( message, self.connection )
        
    def net_requestLoadMap( self, message, **kwargs ):
        networkServer = self.server.networkServerRef()
        playState = networkServer.playStateRef()
        playState.gameLogicManager.preNetworkEvent( message, self.connection )

        self.connection.net_loadMap( self.networkTick, playState.fileName, playState.soundManager.curPlayId )

        playState.gameLogicManager.postNetworkEvent( message, self.connection )

    def net_everythingIsSet( self, message, **kwargs ):
        networkServer = self.server.networkServerRef()
        playState = networkServer.playStateRef()
        playState.gameLogicManager.preNetworkEvent( message, self.connection )

        client = networkServer.getClientByConnection( self.connection )

        client.readyForUpdates = True

        playState.gameLogicManager.postNetworkEvent( message, self.connection )

    def net_clientGameLogicCall( self, message, **kwargs ):
        networkServer = self.server.networkServerRef()
        playState = networkServer.playStateRef()

        client = networkServer.getClientByConnection( self.connection )

        playState.gameLogicManager.clientCallMethod( client, message.methodName, message.argDict )

    def on_disconnect( self ):
        self.server.networkServerRef().removeClientByConnection( self.connection )

    def on_recive( self, message, **kwargs ):
        print "Unrecognized message: ", message

