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

import extern_modules.pygnetic as pygnetic, networkhandlers, weakref, extern_modules.pymunk as pymunk
from genericpolyfuncs import getExtremesAlongAxis, getMidOfPoints
from dictfuncs import getClosestInBounds, filterDict, getClosestKey, getInterpolatedPairValue, getSurroundingValues, getSurroundingKeys

class NetworkClient:
    def __init__( self, playState=None, networkEntsClassDefs=None, conn_limit=1, networkingMode=0, clientSidePrediction=False, clientSideAuthority=True, resimulationMethod=0, *args, **kwargs ):
        self._client = pygnetic.Client( conn_limit, *args, **kwargs )
        
        self.playStateRef = weakref.ref( playState )

        self.networkTick = None

        self.networkEntsClassDefs = networkEntsClassDefs

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

    def connect( self, address, port, message_factory=pygnetic.message.message_factory, **kwargs ):
        self.connection = self._client.connect( address, port, message_factory, **kwargs )
        self.handler = networkhandlers.ClientHandler( self )
        self.connection.add_handler( self.handler )

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
            classDef = self.networkEntsClassDefs[eachTuple[1]]
            destGroup = getattr( self.playStateRef(), classDef.playStateGroup )
            inst = classDef( pos=eachTuple[2], vel=eachTuple[3], group=destGroup )
            inst.id = eachTuple[0]

    def removeEntities( self, removeTuples ):
        playState = self.playStateRef()
        for eachId in [ each[0] for each in removeTuples ]:
            eachEnt = self.findEntById( self, eachId )
            if eachEnt is not None:
                eachEnt.removeFromGroup( *eachEnt.groups() )
        
    def resimulationUsingPymunk( self, startTime, lastAckTime, duration, inputCount, positionTuples, velocityTuples ):
        #So, part of this approximation is that it won't bother remaking everything that was removed from the scene in the mean time, this shouldn't be an issue often however.
        #Work on finding every ent in the ids.
        #print startTime

        playState = self.playStateRef()
        positionDict = dict( positionTuples )
        velocityDict = dict( velocityTuples )

        timeKeys = sorted( playState.stateLog.keys() )
        #If the sent inputCount doesn't match our local one, at that time, then ignore the update.
        #Naaah


        # TODO: This whole thing is toooo daaaamn slow.
        # I need to add indexing to PlayState so this isn't done over and over.
        entDict = {}
        for eachTuple in velocityTuples:
            eachId = eachTuple[0]
            eachEnt = self.findEntById( eachId )
            if eachEnt is None:
                velocityTuples.remove(eachTuple)
            else:
                entDict[eachId] = eachEnt
        #for eachTuple in [ each for each in positionTuples if entDict.get(each[0]) is None ]:
        for eachTuple in [ each for each in positionTuples if each[0] not in entDict.keys() ]:
            eachId = eachTuple[0]
            eachEnt = self.findEntById( eachId )
            if eachEnt is None:
                positionTuples.remove(eachTuple)
            else:
                entDict[eachId] = eachEnt
        #Now, go through every entity, check if the logs are correct, if they're not, flick a boolean and escape the loop.
        resim = False

        #print 'Vel '.join([ str((velocityTuples[each][1], getClosestInBounds(entDict[each].logOfVelocities, startTime))) for each in entDict.keys() ])
        #print 'Pos '.join([ str((positionTuples[each][1], getClosestInBounds(entDict[each].logOfVelocities, startTime))) for each in entDict.keys() ])
        
        for eachTuple in positionTuples:
            eachEnt = entDict[eachTuple[0]]
            #print "Position",
            posAtTime = getClosestInBounds(eachEnt.logOfPositions, startTime)
            #posAtTime = getInterpolatedPairValue(eachEnt.logOfPositions, startTime)
            if posAtTime is None:
                #print sorted( eachEnt.logOfPositions.keys() ), startTime
                continue
            if posAtTime is not None:
                #print "Position"
                #print eachTuple[1]
                deltaPos = eachTuple[1][0]-posAtTime[0], eachTuple[1][1]-posAtTime[1]
                #print deltaPos
                if abs( deltaPos[0] ) > 1 or abs( deltaPos[1] ) > 1:
                    print "Position"
                    timeOfGottenPos = [ each for each in eachEnt.logOfPositions.keys() if eachEnt.logOfPositions[each] == posAtTime ]
                    #surroundingTimes = getSurroundingKeys( eachEnt.logOfPositions, startTime )
                    print posAtTime, eachTuple[1], startTime, timeOfGottenPos, [ ( eachKey, eachEnt.logOfPositions[eachKey] ) for eachKey in sorted( eachEnt.logOfPositions.keys() ) ]#]eachEnt.logOfPositions
                    #for eachKey, eachVal in eachEnt.logOfPositions.items():
                    #    if eachVal == eachTuple[1]:
                    #        print 'trueTime', eachKey, startTime-eachKey#timeOfGottenPos[0]-eachKey
                    #print eachEnt.logOfPositions[timeKeys.index(posAtTime)-1], eachEnt.logOfPositions[timeKeys.index(posAtTime)+1]
                    resim = True
                    break
        if resim == False:
            for eachTuple in velocityTuples:
                eachEnt = entDict[eachTuple[0]]
                #print "Velocity",
                velAtTime = getClosestInBounds(eachEnt.logOfVelocities, startTime)
                #velAtTime = getInterpolatedPairValue(eachEnt.logOfVelocities, startTime)
                if velAtTime is None:
                    continue
                #print "Velocity"
                #print eachTuple[1]
                deltaVel = eachTuple[1][0]-velAtTime[0], eachTuple[1][1]-velAtTime[1]
                deltaPos = deltaVel[0]*(self.timer-startTime), deltaVel[1]*(self.timer-startTime)
                if abs( deltaPos[0] ) > 1 or abs( deltaPos[1] ) > 1:
                    print "Velocity"
                    resim = True
                    #timeOfGottenPos = [ each for each in eachEnt.logOfVelocities.keys() if eachEnt.logOfVelocities[each] == velAtTime ]
                    #print velAtTime, eachTuple[1], startTime, timeOfGottenPos, eachEnt.logOfVelocities    
                    #for eachKey, eachVal in eachEnt.logOfVelocities.items():
                    #    if eachVal == eachTuple[1]:
                    #        print 'trueTime', eachKey, timeOfGottenPos[0]-eachKey
                    #print eachEnt.logOfPositions[timeKeys.index(velAtTime)-1], eachEnt.logOfPositions[timeKeys.index(velAtTime)+1]
                    break
        
        for eachKey in playState.clientSideCorrectionInputBuffer.keys():
            if eachKey < (startTime):
                del playState.clientSideCorrectionInputBuffer[eachKey]
        for eachEnt in entDict.values():
            #eachEnt.logOfPositions = dict( [ (eachTime, eachEnt.logOfPositions
            eachEnt.logOfPositions = filterDict( eachEnt.logOfPositions, lambda x: x >= startTime )
            if eachEnt.collidable:
                eachEnt.logOfVelocities = filterDict( eachEnt.logOfVelocities, lambda x: x >= startTime )

        if resim:
            print "Resimulating, startTime:", startTime, "duration:", duration, "self.timer", self.timer
            #Set everything how it was. By purging everything!

            for eachGroup in playState.groups:
                eachGroup.remove( *eachGroup.sprites() )


            #timeKeys = sorted( playState.stateLog.keys() )
            
            #startIndex = timeKeys.index( startTime ) + 1
            #startIndex = timeKeys.index( getClosestKey( playState.stateLog, startTime ) )
            #if timeKeys[startIndex] < startTime:
            #    startIndex += 1
            #timeKeys = timeKeys[startIndex:]
            #timeKeys.insert(0, startTime)
            timeKeys = [ each for each in timeKeys if each > startTime ]
            timeKeys.insert(0, startTime)
            startIndex = 1
            
            classDefs = playState.devMenuRef().masterEntSet.getEnts()
            classDefsDict = dict( [ ( eachClass.__name__, eachClass ) for eachClass in classDefs ] )
            classDefsDict.update( self.networkEntsClassDefs )
            #for eachGhost in playState.stateLog[startTime]:
            #for eachGhost in getClosestInBounds( playState.stateLog, startTime ):
            for eachGhost in getSurroundingValues( playState.stateLog, startTime )[0]:
                if eachGhost.collidable:
                    eachGhost.bodyGhost.position = positionDict[eachGhost.id][0], positionDict[eachGhost.id][1]
                    eachGhost.loc = eachGhost.bodyGhost.position
                    eachGhost.bodyGhost.velocity = velocityDict[eachGhost.id]
                else:
                    eachGhost.loc = positionDict[eachGhost.id][0], positionDict[eachGhost.id][1]
                eachGhost.resurrectNetworked( classDefsDict, playState )

            self.timer = timeKeys[startIndex]
            tmpInputBuffer = dict( playState.clientSideCorrectionInputBuffer )
            playState.stateLog = dict()
            #Now, LOG PURGE
            #for eachKey in playState.clientSideCorrectionInputBuffer.keys():
            #    if eachKey < (startTime):
            #        del playState.clientSideCorrectionInputBuffer[eachKey]

            for eachIndex in range( startIndex, len( timeKeys ) ):
                eachTime = timeKeys[eachIndex]
                dt = eachTime-timeKeys[eachIndex-1]
                inputDicts = tmpInputBuffer.get( eachTime )
                
                if inputDicts is None:
                    inputDicts = []
                playState.resimulationUpdate( dt, eachTime, inputDicts )
        else:
            #playState.stateLog = dict( [ (eachKey, playState.stateLog[eachKey]) for eachKey in playState.stateLog.keys() if eachKey >= startTime ] )
            print "Everything's fine."
            playState.stateLog = filterDict( playState.stateLog, lambda x: x >= startTime )
        #self.needToFullyResimulate = False

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
        
        
