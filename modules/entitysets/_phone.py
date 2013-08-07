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

from entity import Entity
import pygame
from imageload import loadImage, loadImageNoAlpha

from masterentityset import *

import math

class Phone( Entity ):
    width = 18
    height = 18

    playStateGroup = "genericStuffGroup"
    setName = "genericstuff"

    sheetFileName = "phone.png"
    sheet = loadImageNoAlpha( sheetFileName, 2 )
    specialCollision = None
    scale = 2

    instanceSpecificVars = None
    
    def __init__( self, pos = [0,0], vel = [0,0], group=None, **kwargs ):
        Entity.__init__( self, pos, [0,0], None, group, pygame.Rect( 0, 0, self.width, self.height ), animated=False, **kwargs )
        if Phone.instanceSpecificVars is None:
            attrList = list( self.__dict__.keys() )
        if Phone.instanceSpecificVars is None:
            Phone.instanceSpecificVars = dict( [ ( eachKey, eachVal ) for eachKey, eachVal in self.__dict__.items() if eachKey not in attrList ] )
    
    def update( self, dt ):
        Entity.update( self, dt )
        

#MasterEntitySet.entsToLoad.append( Phone )
entities = { "Phone":Phone }
