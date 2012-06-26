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
	def __init__( self, fileName, priority, soundMgr ):
		self.fileName = fileName
		pygame.mixer.Sound.__init__( self, fileName )
		self.soundManagerRef = weakref.ref( soundMgr )
		self.priority = priority
		
	def play( self, loops=0, maxtime=0, fade_ms=0 ):
		sndMgr = self.soundManagerRef()
		destChannel, channelId = sndMgr.getChannel( self.priority )
		if destChannel is not None:
			destChannel.play(self, loops, maxtime, fade_ms )
			return channelId
		return None

	def stop( self, channelId ):
		pygame.mixer.Channel(channelId).stop()

	def makePicklable( self ):
		self.soundManagerRef = None

	def makeUnpickable( self, sndMgr ):
		self.soundManagerRef = weakref.ref( sndMgr )
		pygame.mixer.Sound.__init__( self, self.fileName )

class SoundManager:
	def __init__( self ):
		self.sounds = {}
		self.path = os.path.join( "data", "sounds" )
		self.channelCount = pygame.mixer.get_num_channels()
		self.channels = [ pygame.mixer.Channel(idNum) for idNum in range( self.channelCount ) ]

	def getSound( self, fileName, priority ):
		key = fileName+str(priority)
		if self.sounds.has_key( key ):
			return self.sounds[key]()
		tmpSound = Sound( os.path.join( self.path, fileName ), priority, self )
		self.sounds[key] = weakref.ref( tmpSound )
		return tmpSound

	def makePicklable( self ):
		self.channels = None
		for eachKey, eachVal in self.sounds.items():
			self.sounds[eachKey] = eachVal()
		for eachSound in self.sounds.values():
			eachSound.makePicklable()

	def makeUnpicklable( self ):
		self.channels = [ pygame.mixer.Channel(idNum) for idNum in range( self.channelCount ) ]
		for eachSound in self.sounds.values():
			eachSound.makeUnpickable( self )
		for eachKey, eachVal in self.sounds.items():
			self.sounds[eachKey] = weakref.ref( eachVal )

	def getChannel( self, priority ):
		#attempt = pygame.mixer.find_channel()
		#if attempt is not None:
		#	return attempt
		#lowest = min( self.channels, key=lambda x, y: cmp( x.get_sound().priority, y.get_sound().priority ) )
		#if lowest <= priority:
		#	return lowest 
		#return None
		curGroup = (priority, 0, None)
		for eachId, eachChannel in enumerate( self.channels ):
			curSound = eachChannel.get_sound()
			if curSound is None:
				return eachChannel, eachId
			if curSound.priority <= curGroup[0]:
				curGroup = (curSound.priority, eachId, eachChannel)
		return curGroup[2], curGroup[1]
