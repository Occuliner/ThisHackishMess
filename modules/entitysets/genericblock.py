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

from entity import *
import pygame
from pygame.locals import *

from masterentityset import *

import math

class GenericBlock( Entity ):
    scale = 2
    width = 32
    height = 32
    bWidth = width
    bHeight = height
    bdx = 0
    bdy = 0
    wbWidth = 32
    wbHeight = 16
    wbdx = 0
    wbdy = 16

    playStateGroup = "genericStuffGroup"
    setName = "genericstuff"

    sheetFileName = "block.png"
    sheet = loadImage( sheetFileName, scale )

    specialCollision = None
    collidable = True
    solid = True
    mass = 20

    instanceSpecificVars = None
    
    def __init__( self, pos = [0,0], vel = [0,0], group=None, **kwargs ):
        Entity.__init__( self, pos, [0,0], None, group, pygame.Rect( 0, 0, self.width, self.height ), animated=False, **kwargs )
        if GenericBlock.instanceSpecificVars is None:
            attrList = list( self.__dict__.keys() )
        if GenericBlock.instanceSpecificVars is None:
            GenericBlock.instanceSpecificVars = dict( [ ( eachKey, eachVal ) for eachKey, eachVal in self.__dict__.items() if eachKey not in attrList ] )
    
    def update( self, dt ):
        Entity.update( self, dt )

MasterEntitySet.entsToLoad.append( GenericBlock )
