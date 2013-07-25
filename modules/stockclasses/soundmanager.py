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

import pygame, weakref, os

from idsource import IdSource

pygame.mixer.init()

class Sound:
    def __init__( self, fileName, soundMgr ):
        self.fileName = fileName
        self._pygameSound = pygame.mixer.Sound( os.path.join( soundMgr.path, fileName ) )
        self.soundManagerRef = weakref.ref( soundMgr )
        self.volume = self._pygameSound.get_volume()

    def set_volume( self, value ):
        self.volume = value
        self._pygameSound.set_volume( value )

    def play( self, priority, loops=0, maxtime=0, fade_ms=0, forceNoPlay=False ):
        sndMgr = self.soundManagerRef()
        if sndMgr.playStateRef().isHost:
            sndMgr.playStateRef().networkNode.addStartSound( self.fileName, priority, loops, maxtime, fade_ms )
        inst = PlayInstance( self, sndMgr.curTime, priority, loops, maxtime, fade_ms, forceNoPlay )
        sndMgr.curPlayId = inst.playId
        if not (inst.channelId is None):
            return inst.playId
                
        return None

    def stop( self, playId ):
        self.soundManagerRef().stopSound( self.fileName, playId )

    def makePicklable( self ):
        self.soundManagerRef = None
        self._pygameSound = None

    def makeUnpickable( self, sndMgr ):
        self.soundManagerRef = weakref.ref( sndMgr )
        self._pygameSound = pygame.mixer.Sound( os.path.join( sndMgr.path, self.fileName ) )
        self._pygameSound.set_volume( self.volume )

class PlayInstance:
    """So, this is a bit of an abstract class, basically the idea is that when a sound is played it creates a play instance.
    The play instance is stored by the soundManager. Each play instance ideally only exists whilst actually playing, to 
    achieve this, each instance keeps track of a "end time" stamp, the product of the amount of times the sound will play
    and the sound's length. The SoundManager will be updated by the playState update method, and the soundManager will keep
    track of what time it is and phase out unneeded play instances when appropriate.

    Upon saving, a list of the SoundManager's current playInstances will be dumped into the save. This can then be used to restore
    the audio state after load.

    The "forceNoPlay" parameter seems really weird, but it's for starting sounds midway through their run, such as on connect to
    a server."""
    def __init__( self, sound, curTime, priority, loops, maxtime, fade_ms, forceNoPlay=False ):
        if loops != -1:
            self.endTime = sound._pygameSound.get_length()*(loops+1) + curTime
        else:
            self.endTime = None
        self.soundFileName = sound.fileName
        self.soundManagerRef = sound.soundManagerRef

        self.loops = loops
        self.maxtime = maxtime
        self.fade_ms = fade_ms

        self.channelId = self.soundManagerRef().getChannel( priority )
        self.playId = self.soundManagerRef().idGen.getId()
        if not forceNoPlay:
            self.attemptPlay( sound._pygameSound )

        self.priority = priority
        
    def attemptPlay( self, sound ):
        """This method attempts to start the sound playing, and if successful adds it the in the list of playing PlayInstances"""
        if not (self.channelId is None):
            pygame.mixer.Channel(self.channelId).play( sound, self.loops, self.maxtime, self.fade_ms )
            self.soundManagerRef().playInstances.append( self )

    def attemptRestart( self, sound ):
        """This method attempts to restart the sound playing after load, and if successful adds it the in the list of playing PlayInstances.
        Currently it cheats and just restarts any looping sound from the nearest loop number"""
        if not (self.channelId is None):
            if self.loops is 0:
                #Create a version of the sound that starts at this moment.
                tmpArray = pygame.sndarray.array( sound )
                start = ( 1 - ( float(self.endTime - self.soundManagerRef().curTime)/sound.get_length() ) )*tmpArray.shape[0]
                splitSound = pygame.sndarray.make_sound( tmpArray[start:] )
                
                pygame.mixer.Channel(self.channelId).play( splitSound, 0, self.maxtime, self.fade_ms )
            elif self.loops is -1:
                pygame.mixer.Channel(self.channelId).play( sound, -1, self.maxtime, self.fade_ms )
            else:
                newLoopNum = (self.loops*(self.endTime - self.soundManagerRef().curTime))/sound.get_length()
                pygame.mixer.Channel(self.channelId).play( sound, newLoopNum, self.maxtime, self.fade_ms )
            playInsts = self.soundManagerRef().playInstances
            if not ( self in playInsts):
                playInsts.append( self )

    def absent( self ):
        """This method returns true if the channel this instance is on is currently not busy"""
        return not pygame.mixer.Channel(self.channelId).get_busy()


    def checkTime( self, curTime ):
        """This method merely returns True if the given curTime is greater than self.endTime"""
        if self.endTime is None:
            return False
        return self.endTime<curTime

    def makePicklable( self ):
        self.soundManagerRef = None

    def makeUnpicklable( self, sndMgr ):
        """Called during loading process, this should restart all sounds"""
        self.soundManagerRef = weakref.ref( sndMgr )
        self.attemptRestart( self.soundManagerRef().getSound( self.soundFileName )._pygameSound )
        
class SoundManager:
    def __init__( self, playState, curTime=0.0 ):
        self.sounds = {}
        self.path = os.path.join( "data", "sounds" )
        self.channelCount = pygame.mixer.get_num_channels()
        self.channels = [ pygame.mixer.Channel(idNum) for idNum in range( self.channelCount ) ]
        self.playInstances = []
        self.curTime = curTime
        self.playStateRef = weakref.ref( playState )
        self.idGen = IdSource()
        self.curPlayId = 0

    def update( self, dt ):
        """Basically all this method does is remove playInstances that are no longer valid."""
        self.curTime += dt
        
        removeList = []
        for eachInst in self.playInstances:
            if eachInst.checkTime( self.curTime ):
                removeList.append( eachInst )
            elif eachInst.absent():
                eachInst.attemptRestart( self.getSound( eachInst.soundFileName )._pygameSound )

        [ self.playInstances.remove( each ) for each in removeList ]

    def getSound( self, fileName ):
        if self.sounds.has_key( fileName ):
            snd = self.sounds[fileName]()
            if not (snd is None):
                return snd
            else:
                print "Reference to None in soundManager.sounds?"
        tmpSound = Sound( fileName, self )
        self.sounds[fileName] = weakref.ref( tmpSound )
        return tmpSound

    def makePicklable( self ):
        self.channels = None
        self.playStateRef = None
        for eachKey, eachVal in self.sounds.items():
            self.sounds[eachKey] = eachVal()
        for eachSound in self.sounds.values():
            eachSound.makePicklable()
        for eachInst in self.playInstances:
            eachInst.makePicklable()

    def makeUnpicklable( self, playState ):
        self.playStateRef = weakref.ref( playState )
        self.channelCount = pygame.mixer.get_num_channels()
        self.channels = [ pygame.mixer.Channel(idNum) for idNum in range( self.channelCount ) ]
        for eachSound in self.sounds.values():
            eachSound.makeUnpickable( self )
        for eachKey, eachVal in self.sounds.items():
            self.sounds[eachKey] = weakref.ref( eachVal )
        for eachInst in self.playInstances:
            eachInst.makeUnpicklable( self )

    def getChannel( self, priority ):
        usedChannelIds = [ each.channelId for each in self.playInstances ]
        if len( usedChannelIds ) < self.channelCount:
            for val in xrange( self.channelCount ):
                if not (val in usedChannelIds):
                    return val
        for eachInst in self.playInstances:
            if eachInst.priority <= priority:
                channel = pygame.mixer.Channel( eachInst.channelId )
                channel.stop()
                return eachInst.channelId

    def stopSound( self, soundName, idNum ):
        if self.playStateRef().isHost:
            self.playStateRef().networkNode.addStopSound( soundName, idNum )
        for each in self.playInstances[:]:
            if each.playId is idNum and each.soundFileName == soundName:
                pygame.mixer.Channel(each.channelId).stop()
                self.playInstances.remove( each )
                break
