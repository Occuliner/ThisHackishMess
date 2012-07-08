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

import pygame
from pygame.locals import *

class HudElement:
	colourKey = None
	alpha = True
	scale = 1
	def __init__( self, playState, pos, sheet=None, animated=False, frameSize=None ):
		if sheet is not None:
			self.sheet = sheet
		self.animated = animated
		self.playState = playState
		if animated:
			self.rect = pygame.Rect( (0,0), frameSize )
			self.rect.topleft = pos
		else:
			self.rect = self.sheet.get_rect()
			self.rect.topleft = pos
		self.createFrames()
		self.frame = 0
		self.image = self.frames[self.frame]
		self.defaultAnim = {'fps':1, 'frames':[0]}
		self.curAnimation = self.defaultAnim
		self.maxFrameTime = 1.000/self.curAnimation['fps']
		self.frameTime = self.maxFrameTime

	def nextFrame( self ):
		self.frame += 1
		if self.frame > len(self.curAnimation['frames']) - 1:
			self.frame = 0
		self.image = self.frames[ self.curAnimation['frames'][self.frame] ]
	
	def createFrames( self ):
		if not self.animated:
			self.frames = [self.sheet]
			return None
		self.frames = []
		tmpRect = self.rect.copy()
		tmpRect.topleft = ( 0, 0 )
		for y in xrange( 0, self.sheet.get_height(), self.rect.h ):
			if y + self.rect.h <= self.sheet.get_height():
				for x in xrange( 0, self.sheet.get_width(), self.rect.w ):
					if x + self.rect.w <= self.sheet.get_width():
						tmpRect.topleft = (x, y)
						tmpSurface = self.sheet.subsurface( tmpRect )
						tmpSurface.set_colorkey( self.colourKey )
						self.frames.append( tmpSurface )

	def draw( self, surface ):
		surface.blit( self.image, self.rect )

	def update( self, dt ):
		if self.animated:
			self.frameTime -= dt
			if self.frameTime <= 0:
				self.nextFrame()
				self.frameTime = self.maxFrameTime
