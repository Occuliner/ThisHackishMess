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

from entity import *
import pygame
from pygame.locals import *

from masterentityset import *

class Toilet( Entity ):
    width = 16
    height = 21

    playStateGroup = "genericStuffGroup"
    setName = "genericstuff"

    sheetFileName = "toilet.png"
    colourKey = pygame.Color( 255, 0, 255 )
    sheet = loadImageNoAlpha( sheetFileName, 2 )
    sheet.set_colorkey( colourKey )

    specialCollision = None
    collidable = False
    scale = 2

    instanceSpecificVars = None

    frameRects = [ pygame.Rect( 0, 0, 32, 42 ), pygame.Rect( 32, 0, 32, 42 ), pygame.Rect( 64, 0, 22, 42 ), pygame.Rect( 86, 0, 22, 42 ) ]
    
    def __init__( self, pos = [0,0], vel = [0,0], group=None, **kwargs ):
        Entity.__init__( self, pos, [0,0], None, group, pygame.Rect( 0, 0, self.width, self.height ), animated=True, **kwargs )
        self.animations['left'] = { 'fps': 1, 'frames':[0] }
        self.animations['right'] = { 'fps': 1, 'frames':[1] }
        self.animations['forward'] = { 'fps': 1, 'frames':[3] }
        self.animations['backward'] = { 'fps': 1, 'frames':[4] }
        self.changeAnimation('left')
        if Toilet.instanceSpecificVars is None:
            attrList = list( self.__dict__.keys() )
        self.oldTag= 'left'
        self.tags['direction'] = 'left'
        if Toilet.instanceSpecificVars is None:
            Toilet.instanceSpecificVars = dict( [ ( eachKey, eachVal ) for eachKey, eachVal in self.__dict__.items() if eachKey not in attrList ] )
    
    def update( self, dt ):
        curTag = self.tags.get('direction')
        if curTag != self.oldTag and curTag in ( 'left', 'right', 'forward', 'backward' ):
            self.changeAnimation(curTag)
            self.oldTag = curTag
        Entity.update( self, dt )

MasterEntitySet.entsToLoad.append( Toilet )
