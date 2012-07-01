from entity import *
from masterentityset import *

import pygame

class EmptyPoint( Entity ):
	width = 32
	height = 32
	setName = "points"
	playStateGroup = "genericStuffGroup"
	collidable = True
	solid = False
	mass = 20
	pureSensor = True
	sheet = pygame.Surface( ( width, height ) ).convert_alpha()
	sheet.fill( pygame.Color( 0, 0, 0, 0 ) )
	pygame.draw.rect( sheet, pygame.Color( 255, 0, 0, 255 ), pygame.Rect( 0, 0, width, height ), 2 )
	def __init__( self, pos=[0,0], vel=[0,0], group=None ):
		Entity.__init__( self, pos, [0,0], None, group, pygame.Rect( 0, 0, self.width, self.height ), animated=False )
		self.visible = 0

MasterEntitySet.entsToLoad.append( EmptyPoint )
