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
from vector import Vector
from tint import tint

from masterentityset import *
    
from imageload import loadImage, loadImageNoAlpha
import pygame

class KickUp( Entity ):
    width = 16
    height = 16
    sheetFileName = "kickup.png"
    sheet = loadImage( sheetFileName, 2 )

    collidable = False
    solid = False

    notDirectlyRemovable = True
    scale = 2

    instanceSpecificVars = None
    
    def __init__( self, group, host ):
        Entity.__init__( self, [0,0], [0,0], None, group, pygame.Rect( 0, 0, self.width, self.height ), animated=True )
        if KickUp.instanceSpecificVars is None:
            attrList = list( self.__dict__.keys() )
        #self.baseSheet = self.sheet.copy()
        self.colour = None

        self.animations['standard'] = { 'fps':8, 'frames':[0,1,2,3] }
        self.changeAnimation( 'standard' )

        #print len(self.frames)


        #self.host = host
        
        if KickUp.instanceSpecificVars is None:
            KickUp.instanceSpecificVars = dict( [ ( eachKey, eachVal ) for eachKey, eachVal in self.__dict__.items() if eachKey not in attrList ] )

    def changeColour( self, colour ):
        self.colour = colour
        tint( self.sheet, colour, original=self.baseSheet )

    def sendInput( self, inputDict ):
        #KickUp will just ignore input.
        pass

    def kill( self ):
        pass
        #You cannot kill the kickUp!

    def specialKill( self ):
        Entity.kill( self )
        #Okay, maybe you can kill the kickUp.

    def update( self, dt ):
        self.setPosition( self.host.standingAt )
        self.position[0] -= self.rect.w/2
        self.position[1] -= (self.rect.h - 1)
        self.rect.topleft = self.getPosition()
        
        Entity.update( self, dt )

#Get where the Yasb is standing
def setStandingAt( entity ):
    entity.standingAt = list( entity.rect.topleft )
    entity.standingAt[0] += int(entity.rect.w/2)
    entity.standingAt[1] += int(entity.rect.h - 3)

class YasbClass( Entity ):
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

    collidable = True
    mass = 70
    specialCollision = None
    solid = True

    instanceSpecificVars = None
    
    def __init__( self, pos = [0,0], vel = [0,0], group=None ):
        Entity.__init__( self, pos, vel, None, group, pygame.Rect( 0, 0, self.width, self.height ), animated=True )
        if YasbClass.instanceSpecificVars is None:
            attrList = list( self.__dict__.keys() )
        
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
        setStandingAt( self )

        #Assign the kickUp!
        #self.kickUp = KickUp( group, self )

        #self.children = [ self.kickUp ]

        self.onKickUpArea = False

        self.groups()[0].change_layer( self, 1 )
        
        if YasbClass.instanceSpecificVars is None:
            YasbClass.instanceSpecificVars = dict( [ ( eachKey, eachVal ) for eachKey, eachVal in self.__dict__.items() if eachKey not in attrList ] )

    def sendInput( self, inputDict ):
        for eachKey, eachVal in inputDict.items():
            if eachKey == 'K_UP':
                if eachVal == 'down':
                    self.walkingForward = True
                elif eachVal == 'up':
                    self.walkingForward = False
            elif eachKey == 'K_DOWN':
                if eachVal == 'down':
                    self.walkingBackward = True
                elif eachVal == 'up':
                    self.walkingBackward = False
            elif eachKey == 'K_LEFT':
                if eachVal == 'down':
                    self.walkingLeft = True
                elif eachVal == 'up':
                    self.walkingLeft = False
            elif eachKey == 'K_RIGHT':
                if eachVal == 'down':
                    self.walkingRight = True
                elif eachVal == 'up':
                    self.walkingRight = False
            #elif eachKey is 'K_RIGHT':
            #    kickUpMap = self.groups()[0].playState.floor.kickUpMap
            #    for y in xrange( 0, kickUpMap.height, 16 ):
            #        row = []
            #        for x in xrange( 0, kickUpMap.width, 32 ):
            #            row.append( int( kickUpMap[x][y] ) )
            #        print row

    def changeColour( self, colour ):
        self.colour = colour
        tint( self.sheet, colour, original=self.baseSheet )
        #theYasb.sheet.fill( pygame.Color( 255, 0, 0 ), special_flags=BLEND_RGB_MULT )
        
    def kill( self ):
        #self.kickUp.specialKill()
        Entity.kill( self )

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
            
        #print "DerP"
        self.body.reset_forces()

        walk = self.applyWalk()
        self.body.apply_force( ( walk[0]*10, walk[1]*10 ) )

        if any( [ self.walkingLeft, self.walkingRight ] ):
            self.idle[0] = False
        if any( [ self.walkingForward, self.walkingBackward ] ):
            self.idle[1] = False
        
        Entity.update( self, dt )

        setStandingAt( self )


#MasterEntitySet.entsToLoad.append( YasbClass )
entities = { "YasbClass":YasbClass }
