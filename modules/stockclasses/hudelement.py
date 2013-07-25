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

import pygame, weakref
from pygame.locals import *
from imageload import loadImageNoAlpha, loadImage

class HudElement:
    colourKey = None
    alpha = True
    scale = 1
    def __init__( self, playState, pos, sheet=None, animated=False, frameSize=None ):
        if sheet is not None:
            self.sheet = sheet
        self.animated = animated
        self.playStateRef = weakref.ref( playState )
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

    def makePicklable( self ):
        self.image = None
        self.sheet = None
        #This is just a forced reference to make sure it should error if you try to save something without this.
        self.sheetFileName = self.sheetFileName
        self.rect = ( self.rect.x, self.rect.y, self.rect.w, self.rect.h )
        self.frames = None
        self.playStateRef = None
        if self.colourKey is not None:
            self.colourKey = self.colourKey.r, self.colourKey.g, self.colourKey.b

    def makeUnpicklable( self, playState ):
        if self.alpha:
            self.sheet = loadImage( self.sheetFileName, self.scale )
        else:
            self.sheet = loadImageNoAlpha( self.sheetFileName, self.scale )
        if self.colourKey is not None:
            self.colourKey = pygame.Color( self.colourKey[0], self.colourKey[1], self.colourKey[2] )
            self.sheet.set_colorkey( self.colourKey )
        self.rect = pygame.Rect( self.rect[0], self.rect[1], self.rect[2], self.rect[3] )
        self.createFrames()
        self.image = self.frames[ self.curAnimation['frames'][self.frame] ]
        self.playStateRef = weakref.ref( playState )
        
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

    def sendInput( self, inputDict ):
        pass

    def update( self, dt ):
        if self.animated:
            self.frameTime -= dt
            if self.frameTime <= 0:
                self.nextFrame()
                self.frameTime = self.maxFrameTime
