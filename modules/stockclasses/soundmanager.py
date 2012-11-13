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

import pygame, weakref, os

pygame.mixer.init()

class Sound( pygame.mixer.Sound ):
	def __init__( self, fileName, soundMgr ):
		self.fileName = fileName
		pygame.mixer.Sound.__init__( self, fileName )
		self.soundManagerRef = weakref.ref( soundMgr )
		self.volume = self.get_volume()

	def set_volume( self, value ):
		self.volume = value
		pygame.mixer.Sound.set_volume( self, value )

	def play( self, priority, loops=0, maxtime=0, fade_ms=0 ):
		sndMgr = self.soundManagerRef()
		inst = PlayInstance( self, sndMgr.curTime, priority, loops, maxtime, fade_ms )
		if not (inst.channelId is None):
			return inst.channelId
		return None

	def stop( self, channelId ):
		pygame.mixer.Channel(channelId).stop()

	def makePicklable( self ):
		self.soundManagerRef = None

	def makeUnpickable( self, sndMgr ):
		self.soundManagerRef = weakref.ref( sndMgr )
		pygame.mixer.Sound.__init__( self, self.fileName )
		pygame.mixer.Sound.set_volume( self, self.volume )

class PlayInstance:
	"""So, this is a bit of an abstract class, basically the idea is that when a sound is played it creates a play instance.
	The play instance is stored by the soundManager. Each play instance ideally only exists whilst actually playing, to 
	achieve this, each instance keeps track of a "end time" stamp, the product of the amount of times the sound will play
	and the sound's length. The SoundManager will be updated by the playState update method, and the soundManager will keep
	track of what time it is and phase out unneeded play instances when appropriate.

	Upon saving, a list of the SoundManager's current playInstances will be dumped into the save. This can then be used to restore
	the audio state after load."""
	def __init__( self, sound, curTime, priority, loops, maxtime, fade_ms ):
		self.endTime = sound.get_length()*(loops+1) + curTime
		self.soundFileName = sound.fileName
		self.soundManagerRef = sound.soundManagerRef

		self.loops = loops
		self.maxtime = maxtime
		self.fade_ms = fade_ms

		self.channelId = self.soundManagerRef().getChannel( priority )
		self.attemptPlay( sound )
		
	def attemptPlay( self, sound ):
		"""This method attempts to start the sound playing, and if successful adds it the in the list of playing PlayInstances"""
		if not (self.channel is None):
			pygame.mixer.Channel(self.channelId).play( sound, self.loops, self.maxtime, self.fade_ms )
			self.soundManagerRef().playInstances.append( self )

	def attemptRestart( self, sound ):
		"""This method attempts to restart the sound playing after load, and if successful adds it the in the list of playing PlayInstances.
		Currently it cheats and just restarts any looping sound from the nearest loop number"""
		if not (self.channel is None):
			if self.loops is 0:
				#Create a version of the sound that starts at this moment.
				tmpArray = pygame.sndarray.array( sound )
				start = ( 1 - ( float(self.endTime - self.soundManagerRef().curTime)/sound.get_length() ) )*tmpArray.shape[0]
				splitSound = pygame.sndarray.make_sound( tmpArray[start:] )
				
				pygame.mixer.Channel(self.channelId).play( splitSound, 0, self.maxtime, self.fade_ms )
			else:
				newLoopNum = (self.loops*(self.endTime - self.soundManagerRef().curTime))/sound.get_length()
				pygame.mixer.Channel(self.channelId).play( sound, newLoopNum, self.maxtime, self.fade_ms )
			self.soundManagerRef().playInstances.append( self )

	def absent( self ):
		"""This method returns true if the channel this instance is on is currently not busy"""
		return not pygame.mixer.Channel(self.channelId).get_busy()


	def checkTime( self, curTime ):
		"""This method merely returns True if the given curTime is greater than self.endTime"""
		return self.endTime<curTime

	def makePicklable( self ):
		self.soundManagerRef = None

	def makeUnpicklable( self, sndMgr ):
		"""Called during loading process, this should restart all sounds"""
		self.soundManagerRef = weakref.ref( sngMgr )
		self.attemptRestart( self.soundManagerRef().getSound( self.soundFileName ) )
		
class SoundManager:
	def __init__( self, curTime=0.0 ):
		self.sounds = {}
		self.path = os.path.join( "data", "sounds" )
		self.channelCount = pygame.mixer.get_num_channels()
		self.channels = [ pygame.mixer.Channel(idNum) for idNum in range( self.channelCount ) ]
		self.playInstances = []
		self.curTime = curTIme

	def update( self, dt ):
		"""Basically all this method does is remove playInstances that are no longer valid."""
		self.curTime += dt
		
		removeList = []
		for eachInst in self.playInstances:
			if eachInst.endTime < self.curTime:
				removeList.append( eachInst )
			if eachInst.absent():
				eachInst.attemptRestart()

		[ self.playInstances.remove( each ) for each in removeList ]

	def getSound( self, fileName ):
		if self.sounds.has_key( fileName ):
			return self.sounds[key]()
		tmpSound = Sound( os.path.join( self.path, fileName ), self )
		self.sounds[key] = weakref.ref( tmpSound )
		return tmpSound

	def makePicklable( self ):
		self.channels = None
		for eachKey, eachVal in self.sounds.items():
			self.sounds[eachKey] = eachVal()
		for eachSound in self.sounds.values():
			eachSound.makePicklable()
		for eachInst in self.playInstances:
			eachInst.makePicklable()

	def makeUnpicklable( self ):
		self.channelCount = pygame.mixer.get_num_channels()
		self.channels = [ pygame.mixer.Channel(idNum) for idNum in range( self.channelCount ) ]
		for eachSound in self.sounds.values():
			eachSound.makeUnpickable( self )
		for eachKey, eachVal in self.sounds.items():
			self.sounds[eachKey] = weakref.ref( eachVal )
		for eachInst in self.playInstances:
			eachInst.makeUnpicklable()

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
