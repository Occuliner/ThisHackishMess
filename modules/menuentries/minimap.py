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

import pygame, os
from button import Button

class MiniMap( Button ):
    pos = ( 800-160, 600-120 )
    def __init__( self, parentState, width, height ):
        Button.__init__( self, None, None, parentState, True )
        self.width = width
        self.height = height
        self.scale = None
        self.floor = parentState.menu.playState.floor
        self.image = self.generateImage()
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos
        self.held = False
        self.heldPos = None
        self.dragging = False
        self.panning = False

    def generateImage( self ):
        rightMostPoint = max( [ each.rect.right for each in self.floor.layers ] )
        leftMostPoint = min( [ each.rect.left for each in self.floor.layers ] )
        topMostPoint = min( [ each.rect.top for each in self.floor.layers ] )
        bottomMostPoint = max( [ each.rect.bottom for each in self.floor.layers ] )
        worldWidth = rightMostPoint-leftMostPoint
        worldHeight = bottomMostPoint-topMostPoint
        sizeRect = pygame.Rect( 0, 0, worldWidth, worldHeight )
        playState = self.parentState.menu.playState
        img = pygame.Surface( (sizeRect.w, sizeRect.h) ).convert()
        for eachLayer in self.floor.layers:
            loc = (eachLayer.rect.left-leftMostPoint, eachLayer.rect.top-topMostPoint)
            img.blit( eachLayer.image, loc )
        scale = 1.0
        if worldWidth > worldHeight:
            scale = float(self.width)/worldWidth
        else:
            scale = float(self.height)/worldHeight
        self.scale = scale
        img = pygame.transform.rotozoom(img, 0.0, scale ).convert()
        #pos = playState.panX*scale, playState.panY*scale
        viewRect = pygame.Rect( playState.panX*scale, playState.panY*scale, 800*scale, 600*scale )
        
        finalImage = pygame.Surface( (self.width, self.height) ).convert()
        finalImage.blit( img, (0, 0) )
        pygame.draw.rect( finalImage, pygame.Color( 255, 0, 0 ), viewRect, 1 )
        pygame.draw.rect( finalImage, pygame.Color( 255, 0, 0 ), pygame.Rect( 0, 0, self.width-1, self.height-1 ), 1 )
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
        playState.panX = int(dx/self.scale)
        playState.panY = int(dy/self.scale)

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
