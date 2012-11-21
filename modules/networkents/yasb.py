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

from networkentity import *
from vector import Vector
from pygame.locals import *
from tint import tint

from mindlessentholder import *
	
class KickUpNetwork( NetworkEntity ):
	width = 16
	height = 16
	sheetFileName = "kickup.png"
	sheet = loadImage( sheetFileName, 2 )

	collidable = False
	solid = False

	notDirectlyRemovable = True
	scale = 2
	
	def __init__( self, group, host ):
		NetworkEntity.__init__( self, [0,0], [0,0], None, group, pygame.Rect( 0, 0, self.width, self.height ), animated=True )
		#self.baseSheet = self.sheet.copy()
		self.colour = None

		self.animations['standard'] = { 'fps':8, 'frames':[0,1,2,3] }
		self.changeAnimation( 'standard' )

	def kill( self ):
		pass
		#You cannot kill the kickUp!

	def specialKill( self ):
		Entity.kill( self )
		#Okay, maybe you can kill the kickUp.

	def update( self, dt ):
		
		NetworkEntity.update( self, dt )


class YasbClassNetwork( NetworkEntity ):
	setName = "players"
	playStateGroup = "playersGroup"
	
	sheetFileName = "yasb.png"
	sheet = loadImage( sheetFileName, 2 )
	scale = 2
	#white = pygame.Color( 255, 255, 255 )

	width = 28
	height = 36
	bWidth = width
	bHeight = height
	bdx = 0
	bdy = 0
	wbWidth = 24
	wbHeight = 16
	wbdx = 2
	wbdy = 20

	mass = 70
	solid = True

	
	def __init__( self, pos = [0,0], vel = [0,0], group=None ):
		NetworkEntity.__init__( self, pos, vel, None, group, pygame.Rect( 0, 0, self.width, self.height ), animated=True )
		
		#self.acceleration[1] = 384
		
		self.randomSound = group.playState.soundManager.getSound( "sfx_step_grass-CCBY.wav" )
		self.randomSound.set_volume( 0.5 )
		
		self.stepsPlaying = False
		self.stepsId = None

		#self.baseSheet = self.sheet.copy()
		
		self.colour = None

		#self.walkSpeed = 194
		#self.walkAccel = 1024
		self.walkAccel = 4096
		
		self.changeMaxVel( 192 )
		
		self.walkingLeft = False
		self.walkingRight = False
		self.walkingForward = False
		self.walkingBackward = False

		self.animations['awesomeWalkY'] = { 'fps':12, 'frames':[1,2,0,2,3,2,0,2] }
		self.animations['walkY'] = { 'fps':8, 'frames':[1,2,3,2] }
		self.animations['walkLeft'] = { 'fps':8, 'frames':[5,6,7,6] }
		self.animations['walkRight'] = { 'fps':8, 'frames':[8,9,10,9] }

		self.walkingAnims = ( self.animations['walkY'], self.animations['walkLeft'], self.animations['walkRight'] )
		
		#self.animations['walkY'] = { 'fps':8, 'frames':[1,3,5,3] }
		#self.animations['spin'] = { 'fps':8, 'frames':[4,1,5,1] }

		self.standingAt = None

		#Assign the kickUp!
		#self.kickUp = KickUp( group, self )

		#self.children = [ self.kickUp ]

		self.onKickUpArea = False

		self.groups()[0].change_layer( self, 1 )
		
	def sendInput( self, inputDict ):
		pass

	def changeColour( self, colour ):
		self.colour = colour
		tint( self.sheet, colour, original=self.baseSheet )
		#theYasb.sheet.fill( pygame.Color( 255, 0, 0 ), special_flags=BLEND_RGB_MULT )
		
	def kill( self ):
		#self.kickUp.specialKill()
		NetworkEntity.kill( self )

	def applyWalk( self ):
		walkingDirection = Vector( 0, 0 )
		if self.walkingLeft:
			walkingDirection += Vector( -1, 0 )
			if self.curAnimation in self.walkingAnims:
				self.swapAnimation( 'walkLeft' )
			else:
				self.changeAnimation( 'walkLeft' )

		if self.walkingRight:
			walkingDirection += Vector( 1, 0 )
			if self.curAnimation in self.walkingAnims:
				self.swapAnimation( 'walkRight' )
			else:
				self.changeAnimation( 'walkRight' )
		if self.walkingForward:
			walkingDirection += Vector( 0, -1 )
			if self.curAnimation in self.walkingAnims:
				self.swapAnimation( 'walkY' )
			else:
				self.changeAnimation( 'walkY' )
			
			#Set the kickup to appear infront of the player when the player is walking towards the top of the screen.
			
			#self.kickUp.groups()[0].change_layer( kickUp, 2 )
			#self.groups()[0].move_to_front( self.kickUp )
			
		if self.walkingBackward:
			walkingDirection += Vector( 0, 1 )
			if self.curAnimation in self.walkingAnims:
				self.swapAnimation( 'walkY' )
			else:
				self.changeAnimation( 'walkY' )
			
			#Set the kickup to appear behind the player when the player is walking towards the bottom of the screen.

			#self.kickUp.groups()[0].change_layer( kickUp, 0 )
			#self.groups()[0].move_to_back( self.kickUp )
			
		if self.walkingLeft or self.walkingRight or self.walkingForward or self.walkingBackward:
			if self.stepsId is None:
				self.stepsId = self.randomSound.play(priority=1, loops=-1)
			if self.onKickUpArea:
				pass
				#self.kickUp.setVisible( True )
			else:
				pass
				#self.kickUp.setVisible( False )
		else:
			if self.stepsId is not None:
				self.randomSound.stop(self.stepsId)
				self.stepsId = None
			self.changeAnimation( 'idle' )
			#self.kickUp.setVisible( False )
		

		if walkingDirection.getSize() != 0:
			resultVector = Vector( self.walkAccel, 0 ).setAngle( walkingDirection.getAngle() )
		else:
			resultVector = Vector( 0, 0 )
		#print resultVector.getSize()

		return resultVector
		
	def draw( self, surface ):
		Entity.draw( self, surface )

	def update( self, dt ):
			
		#self.body.reset_forces()

		#walk = self.applyWalk()
		#self.body.apply_force( ( walk[0]*10, walk[1]*10 ) )

		#if any( [ self.walkingLeft, self.walkingRight ] ):
		#	self.idle[0] = False
		#if any( [ self.walkingForward, self.walkingBackward ] ):
		#	self.idle[1] = False
		
		NetworkEntity.update( self, dt )


MindlessEntHolder.dictOfEnts["YasbClassNetwork"] = YasbClassNetwork
