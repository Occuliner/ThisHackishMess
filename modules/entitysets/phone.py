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
		

MasterEntitySet.entsToLoad.append( Phone )
