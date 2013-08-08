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

import extern_modules.pygnetic as pygnetic, networkhandlers, weakref, extern_modules.pymunk as pymunk
from genericpolyfuncs import getExtremesAlongAxis, getMidOfPoints
from dictfuncs import getClosestInBounds, filterDict, getClosestKey, getInterpolatedPairValue, getSurroundingValues, getSurroundingKeys
from picklestuff import loadPlayState
from idsource import IdSource

class NetworkClient:
    def __init__( self, playState=None, conn_limit=1, networkingMode=0, clientSidePrediction=False, clientSideAuthority=True, resimulationMethod=0, *args, **kwargs ):
        self._client = pygnetic.Client( conn_limit, *args, **kwargs )
        
        self.playStateRef = weakref.ref( playState )

        self.networkTick = None

        self.handler = None

        self.name = "Banana"

        self.connection = None

        self.timer = 0.0

        self.serverTime = 0.0

        self.inputTimeLog = [0.0]

        #Networking mode is whether the client will merely recreate the state as sent from the host, and send input, or use interpolation and/or extrapolation.
        #0=No interoplation/extrapoltion, 1=Extrapolation, 2=Interpolation.
        self.interpolationOn, self.extrapolationOn = False, False
        if networkingMode is 1:
            self.extrapolationOn = True
        elif networkingMode is 2:
            self.interpolationOn = True

        self.clientSidePrediction = clientSidePrediction
        self.clientSideAuthority = clientSideAuthority

        #This is how the client corrects itself when a prediction is wrong.
        #0 is simply teleport to the new location, this causes clipping into objects.
        #1 is using segment queries to move as far towards the new direction until you hit another object.
        #This is inaccurate if you hit into an object that can/would be pushed, and due to segment usage, can clip through smaller objects anyway.
        #2 is to resimulate the series of events, using some approximations (attempts to ignore objects that shouldn't have changed.)
        self.resimulationMethod = resimulationMethod

        #self.givenFirstState = False

        self.needToFullyResimulate = False

        self.messageLog = {}

        self.latencySamples = []
        self.latencySampleSize = 5

        self.clientPlayerIds = []

        self.hostAddr = None
        self.hostPort = None

    def connect( self, address, port, message_factory=pygnetic.message.message_factory, **kwargs ):
        self.connection = self._client.connect( address, port, message_factory, **kwargs )
        self.handler = networkhandlers.ClientHandler( self )
        self.connection.add_handler( self.handler )
        self.hostAddr, self.hostPort = address, port

    def getLatency( self ):
        return float( sum( self.latencySamples ) )/len( self.latencySamples )

    def addLatencySample( self, time ):
        self.latencySamples.append( time )
        if ( len( self.latencySamples ) > self.latencySampleSize ):
            self.latencySamples.pop(0)

    def sendInput( self, inputDict ):
        if self.connection.connected:
            self.connection.net_inputEvent( self.networkTick, self.timer, inputDict )
        self.inputTimeLog.append( self.timer )

    def createEntities( self, createTuples ):
        for eachTuple in createTuples:
            #Needs to swap from NetworkEntities to normal entities.
            classDef = self.playStateRef().devMenuRef().masterEntitySet.getEntityClass( eachTuple[1] )
            if classDef.playStateGroup == "playersGroup":
                destGroup = getattr( self.playStateRef(), "networkPlayers" )
            else:
                destGroup = getattr( self.playStateRef(), classDef.playStateGroup )
           
            inst = classDef( pos=eachTuple[2], vel=eachTuple[3], group=destGroup, **eachTuple[4] )
            inst.id = eachTuple[0]

    def removeEntities( self, removeTuples ):
        playState = self.playStateRef()
        for eachId in [ each[0] for each in removeTuples ]:
            eachEnt = self.findEntById( eachId )
            if eachEnt is not None:
                eachEnt.removeFromGroup( *eachEnt.groups() )

    def findEntById( self, theId ):
        for eachEnt in self.playStateRef().sprites():
            if eachEnt.id == theId:
                return eachEnt
        print "WAT. RECEIVED UPDATE REFERRING TO NON-EXISTANT ENTITY.", 'Cur ents', self.playStateRef().sprites()

    def updatePositions( self, positionTuples, updateTime ):
        playState = self.playStateRef()
        for eachTuple in positionTuples:
            eachId = eachTuple[0]
            eachEnt = self.findEntById( eachId )
            if eachEnt is None or ( eachId in self.clientPlayerIds and self.clientSideAuthority ):
                continue
            if eachEnt.collidable:
                eachEnt.body.activate()
            eachEnt.setPosition( eachTuple[1] )

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
            if eachEnt is not None and not (eachId in self.clientPlayerIds):
                eachEnt.swapAnimation( eachTuple[1] )

    def changeAnims( self, changeTuples ):
        playState = self.playStateRef()
        for eachTuple in changeTuples:
            eachId = eachTuple[0]
            eachEnt = self.findEntById( eachId )
            if eachEnt is not None and not (eachId in self.clientPlayerIds):
                eachEnt.changeAnimation( eachTuple[1] )

    def forceAnims( self, entIdFrameTuples ):
        playState = self.playStateRef()
        for eachTuple in entIdFrameTuples:
            eachId = eachTuple[0]
            eachEnt = self.findEntById( eachId )
            if eachEnt is None or (eachId in self.clientPlayerIds):
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
        for eachTuple in entIdVelocityTuples:
            eachId = eachTuple[0]
            eachEnt = self.findEntById( eachId )
            if eachEnt is None or ( eachId in self.clientPlayerIds and self.clientSideAuthority ):
                continue
            eachEnt.body.velocity.x = eachTuple[1][0]
            eachEnt.body.velocity.y = eachTuple[1][1]
    
    def disconnectAll( self ):
        if self.connection.connected:
            self.connection.disconnect()

    def addToMessageLog( self, message ):
        if self.messageLog.get( self.timer ) == None:
            self.messageLog[self.timer] = []
        self.messageLog[self.timer].append( message )

    def sendPlayerState( self ):
        players = []
        players.extend( self.playStateRef().playersGroup.sprites() )
        for each in self.playStateRef().networkPlayers:
            if each.id in self.clientPlayerIds:
                players.append(each)
        for eachPlayer in players:
            self.connection.net_playerUpdate( self.networkTick, self.serverTime, eachPlayer.id, eachPlayer.getPosition(), eachPlayer.body.velocity.int_tuple )

    def loadMap( self, mapName, playId ):
        #So playId is here to make sure the clients always have the same sound id as the host.
        playState = self.playStateRef()
        if not (mapName is "Untitled"):
            #So, if there is a level name, load that level if found.
            newState = loadPlayState( mapName, playState.floor.tileSet, playState.devMenuRef, networkClient=self )
            if newState is None:
                print "Host was on a level you don't have. Requesting download"
                self.connection.net_requestMapBuffer( self.networkTick, mapName )
                return None
            else:
                playState.swap( newState )
        
        playState.soundManager.idGen = IdSource()
        if playId != 0:
            for each in xrange( playId+1 ):
                playState.soundManager.idGen.getId()
        playState.soundManager.curPlayId = playId
        #On a successful load, request state info.
        self.connection.net_requestState( self.networkTick )

    def update( self, dt, timeout=0 ):
        self._client.update( timeout )
        #self.timer += dt
        if self.clientSideAuthority:
            self.sendPlayerState()

    def updateTime( self, dt ):
        self.timer += dt
        self.serverTime += dt

    def resimulationUpdate( self, dt, curTime, timeout=0 ):
        messages = getClosestInBounds( self.messageLog, curTime )
        if messages is not None:
            for eachMessage in messages:
                getattr( self.handler, "net_" + type( eachMessage ).__name__ )( eachMessage, resimulation=True )
        self.timer += dt

