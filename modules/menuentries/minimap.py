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
    def __init__( self, parentState, pos, width, height ):
        Button.__init__( self, None, None, parentState, True )
        self.width = width
        self.height = height
        self.floor = parentState.menu.playState.floor
        self.image = self.generateImage()
        self.rect = self.image.get_rect()
        self.rect.topleft = pos

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
        img = pygame.transform.rotozoom(img, 0.0, scale ).convert()
        pos = playState.panX*scale, playState.panY*scale
        finalImage = pygame.Surface( (self.width, self.height) ).convert()
        finalImage.blit( img, pos )
        return finalImage

    def regenerateImage( self ):
        tmpLoc = self.rect.topleft
        self.image = self.generateImage()
        self.rect = self.image.get_rect()
        self.rect.topleft = tmpLoc
