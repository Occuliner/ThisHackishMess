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
from pygame.locals import *

from hudelement import HudElement
from imageload import loadImageNoAlpha
from getres import getResolution

def splitFrames( image, size ):
    frames = []
    tmpRect = pygame.Rect( (0,0), size )
    for y in xrange( 0, image.get_height(), size[1] ):
        if y + size[1] <= image.get_height():
            for x in xrange( 0, image.get_width(), size[0] ):
                if x + size[0] <= image.get_width():
                    tmpRect.topleft = (x, y)
                    tmpSurface = image.subsurface( tmpRect )
                    frames.append( tmpSurface )
    return frames

class TextBox( HudElement ):
    alpha = False
    sheetFileName = "textboxsheet.png"
    colourKey = pygame.Color( 255, 0, 255 )
    font = pygame.font.Font( os.path.join( "data", "fonts", "Keenton-CCBY.ttf" ), 24 )
    def __init__( self, playState, text, box=None ):
        sheet = loadImageNoAlpha( self.sheetFileName )
        self.originFrames = splitFrames( sheet, (32, 32) )
        if box is None:
            w, h = getResolution()
            box = pygame.Rect( (0, (7.0/12)*h), (w, (5.0/12)*h ) )
        
        img = pygame.Surface( (box.w, box.h) ).convert()
        #img.fill( pygame.Color( 0, 0, 0, 0 ) )

        for x in range( 32, box.w, 32 ):
            img.blit( self.originFrames[1], (x, 0) )
            img.blit( self.originFrames[7], (x, box.h-32) )

        for y in range( 32, box.h, 32 ):
            img.blit( self.originFrames[3], (0, y) )
            img.blit( self.originFrames[5], (box.w-32, y) )

        for x in range( box.x+32, box.w+box.x-32, 32 ):
            for y in range( 32, box.h-32, 32 ):
                img.blit( self.originFrames[4], (x,y) )
        
        img.blit( self.originFrames[0], ( 0, 0 ) )
        img.blit( self.originFrames[2], (box.w-32, 0) )
        img.blit( self.originFrames[6], (0, box.h-32) )
        img.blit( self.originFrames[8], (box.w-32, box.h-32) )

        wLimit = box.w-64

        subStrings = []
        lastIndex = 0
        for eachIndex in range( len( text ) ):
            eachSub = text[lastIndex:eachIndex]
            if text[eachIndex] == "\n":
                subStrings.append( eachSub )
                lastIndex = eachIndex + 1
            elif self.font.size( eachSub )[0] > wLimit:
                subStrings.append( eachSub[:-1] )
                lastIndex = eachIndex - 1
            elif eachIndex == ( len( text ) - 1 ):
                subStrings.append( eachSub+text[-1] )
        if len( subStrings ) is  0:
            subStrings = [ text ]

        curIndex = 0
        curY = 32
        while curY < box.h-32 and curIndex < len( subStrings ):
            eachImg = self.font.render( subStrings[curIndex], True, pygame.Color( 0, 0, 0 ) )
            img.blit( eachImg, ( 32, curY ) )
            curY += eachImg.get_height()
            curIndex += 1

        HudElement.__init__( self, playState, box.topleft, img, False )
        self.image.set_colorkey( self.colourKey )

        self.dying = False
        self.removed = False
        self.removeTime = 0.5
        self.removeTimer = 0.0

        self.borning = True
        self.bornTime = 0.25
        self.bornTimer = 0.0
        
    def sendInput( self, inputDict ):
        for eachKey, eachVal in inputDict.items():
            if eachKey in ( 'K_c', 'K_x', 'K_z' ):
                if eachVal is 'up':
                    self.dying = True

    def update( self, dt ):
        HudElement.update( self, dt )
        if self.dying:
            #self.image.set_alpha( int( 255*( 1.0-( self.removeTimer/self.removeTime) ) ) )
            ratio = ( ( ( self.removeTimer-self.removeTime )**2 )/(self.removeTime**2) )
            self.image.set_alpha( int( 255*ratio ) )
            self.removeTimer += dt
            if self.removeTimer > self.removeTime:
                self.playStateRef().hudList.remove( self )
                self.removed = True
                self.dying = False
                self.removeTimer = 0.0
        elif self.borning:
            ratio = ( ( ( self.bornTimer-self.bornTime )**2 )/(self.bornTime**2) )
            self.image.set_alpha( int( 255*ratio ) )
            self.bornTimer += dt
            if self.bornTimer > self.bornTime:
                self.borning = False
                self.bornTimer = 0.0
