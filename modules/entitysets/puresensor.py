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

from masterentityset import *

class PureSensor( Entity ):
    setName = "pureSensors"
    playStateGroup = "genericStuffGroup"
    collidable = True
    solid = False
    mass = 20
    pureSensor = True
    sheet = pygame.Surface( ( 1, 1 ) ).convert_alpha()
    sheet.fill( pygame.Color( 0, 0, 0, 0 ) )
    sheetFileName = None
    notDirectlyRemovable = True

    instanceSpecificVars = None
    def __init__( self, pos=[0,0], vel=[0,0], group=None, width=0, height=0, **kwargs ):
        Entity.__init__( self, pos, [0,0], None, group, pygame.Rect( 0, 0, width, height ), animated=False, **kwargs )
        self.visible = 0
        if PureSensor.instanceSpecificVars is None:
            attrList = list( self.__dict__.keys() )
        
        self.w, self.h = width, height
        if PureSensor.instanceSpecificVars is None:
            PureSensor.instanceSpecificVars = dict( [ ( eachKey, eachVal ) for eachKey, eachVal in self.__dict__.items() if eachKey not in attrList ] )

MasterEntitySet.entsToLoad.append( PureSensor )
