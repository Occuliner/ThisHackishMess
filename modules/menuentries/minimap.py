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

import pygame, os
from button import Button
from getres import getResolution

class MiniMap( Button ):
    pos = None
    def __init__( self, parentState, width, height ):
        Button.__init__( self, None, None, parentState, True )
        self.width = width
        self.height = height
        self.scale = None
        self.image = self.generateImage()
        self.rect = self.image.get_rect()
        if self.pos is None:
             MiniMap.pos = ( getResolution()[0]-width, getResolution()[1]-height )
        self.rect.topleft = self.pos
        self.held = False
        self.heldPos = None
        self.dragging = False
        self.panning = False

    def getFloor( self ):
        return self.parentState.menu.playState.floor

    def generateImage( self ):
        floor = self.getFloor()
        rightMostPoint = max( [ each.rect.right for each in floor.layers ] )
        leftMostPoint = min( [ each.rect.left for each in floor.layers ] )
        topMostPoint = min( [ each.rect.top for each in floor.layers ] )
        bottomMostPoint = max( [ each.rect.bottom for each in floor.layers ] )
        worldWidth = rightMostPoint-leftMostPoint
        worldHeight = bottomMostPoint-topMostPoint
        sizeRect = pygame.Rect( 0, 0, worldWidth, worldHeight )
        playState = self.parentState.menu.playState
        img = pygame.Surface( (sizeRect.w, sizeRect.h) ).convert()
        for eachLayer in floor.layers:
            loc = (eachLayer.rect.left-leftMostPoint, eachLayer.rect.top-topMostPoint)
            img.blit( eachLayer.image, loc )
        scale = 1.0
        if worldWidth > worldHeight:
            scale = float(self.width)/worldWidth
        else:
            scale = float(self.height)/worldHeight
        self.scale = scale
        img = pygame.transform.rotozoom(img, 0.0, scale ).convert()
        screenW, screenH = getResolution()
        viewRect = pygame.Rect( (-leftMostPoint)*scale, (-topMostPoint)*scale, screenW*scale, screenH*scale )
        finalImage = pygame.Surface( (self.width, self.height) ).convert()
        finalImage.blit( img, (0, 0) )
        pygame.draw.rect( finalImage, pygame.Color( 255, 0, 0 ), viewRect, 1 )
        pygame.draw.rect( finalImage, pygame.Color( 255, 0, 0 ), pygame.Rect( 0, 0, self.width, self.height ), 1 )
        return finalImage

    def regenerateImage( self ):
        tmpLoc = self.rect.topleft
        self.image = self.generateImage()
        self.rect = self.image.get_rect()
        self.rect.topleft = tmpLoc

    def pan( self, point ):
        dx = float(point[0]-self.rect.left)
        dy = float(point[1]-self.rect.top)
        playState = self.parentState.menu.playState
        screenW, screenH = getResolution()
        playState.setPan( -int(dx/self.scale)+(screenW/2), -int(dy/self.scale)+(screenH/2) )

    def push( self, clickKey, click ):
        self.held = True
        self.heldPos = click[0]-self.rect.left, click[1]-self.rect.top
        if "down" in clickKey:
            if "mouse1" in clickKey:
                self.panning = True
            if "mouse3" in clickKey:
                self.dragging = True
        if "up" in clickKey:
            self.held = False
            self.heldPos = None
            self.dragging = False
            self.panning = False
