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

import pygame, extern_modules.pymunk as pymunk, weakref, math

from imageload import loadImage, loadImageNoAlpha
from imageslice import sliceImage

class EntityGroup( pygame.sprite.LayeredDirty ):
    def __init__( self, name="Unnamed" ):
        pygame.sprite.LayeredDirty.__init__( self )
        self.name = name
        self.playState = None
    def add( self, *sprites, **kwargs ):
        for sprite in sprites:
            if sprite.collidable:
                self.playState.space.add( sprite.physicsObjects )
            sprite.id = self.playState.idSource.getId()
            
        pygame.sprite.LayeredDirty.add( self, sprites, kwargs )
        

    def remove( self, *sprites, **kwargs ):
        for sprite in sprites:
            if sprite.collidable:
                self.playState.space.remove( sprite.physicsObjects )
            sprite.id = None
            
        pygame.sprite.LayeredDirty.remove( self, sprites, kwargs )

    def update( self, dt ):
        for each in iter( self ):
            each.update( dt )
            
def idleCentricVelocityUpdateNoGrav( body, gravity, damping, dt ):
    """
    Same as above, but without gravity.
    """
    if body.force.x == 0 and body.force.y == 0:
        pymunk.Body.update_velocity( body, 0.0, damping, dt )
    else:
        pymunk.Body.update_velocity( body, 0.0, 1.0, dt )
    dx = abs(body.velocity.x)-body.xLimit
    dy = abs(body.velocity.y)-body.yLimit
    if dx > 0:
        body.velocity.x -= dx
    if dy > 0:
        body.velocity.y -= dy

def noGravVelocityUpdate( body, gravity, damping, dt ):
    """Standard Vel update, but without gravity."""
    pymunk.Body.update_velocity( body, [0.0, 0.0], damping, dt )

def velocityUpdateWrapped( body, gravity, damping, dt):
    pymunk.Body.update_velocity( body, gravity, damping, dt )

def idleCentricVelocityUpdate( body, gravity, damping, dt ):
    """
    This function is an "idle-centric" velocity updater for Pymunk.

    Basically it means that objects only have their velocity "dampen" when no net force is being exerted on them.
    """
    if body.force.x == 0 and body.force.y == 0:
        pymunk.Body.update_velocity( body, gravity, damping, dt )
    else:
        pymunk.Body.update_velocity( body, gravity, 1.0, dt )

class Entity( pygame.sprite.DirtySprite ):
    
    #If this is true on an entity, then it will neither appear in the Entity Edit menu nor be editable in the Entity Edit Menu.
    notEditable = False

    mass = 1
    
    #Set this just so that everything has a sheetFileName attr, really each class should specify its own one.
    sheetFileName = None

    #Width and Height are for the frames, bWidth and bHeight for sensor boxes, wbWidth and wbHeight for "physics" boxes.
    width, height, bWidth, bHeight, wbWidth, wbHeight = None, None, None, None, None, None
    bdx, bdy = 0, 0

    #If something is only a sensor with no visual appearance.
    pureSensor = False

    #If something is only ever gong to a sensor, but can be visual.
    neverCollides = False

    #The scale of the sprite's sheet from it's default file.
    scale = 1

    #RGB colourKey. Look it up on Pygame.
    colourKey = None

    #Does exactly what it says on the tin.
    ignoreGravity = False

    #Whether the sprite uses per-pixel alpha
    alpha = True
    
    #Force Use Rect tells the EntityEdit menu to use the frame size for grabbing an image from the spritesheet to display, rather than BoundingBox or WalkBox, which the menu will generally prefer.
    forceUseRect = False

    #FrameRects are all the rect areas to cut for frames, in index order, if left as none, it auto-slices.
    frameRects = None

    #Frame Positions are the x-position and y-position of the each frame relative to the physics body, (0,0) is the center is positioned on body location, this is the default and typical state.
    framePositions = {}

    #If this flag is set to true, then this entity in ghost form is stored by its parent, not by the usual methods.
    isChild = False

    #Important params. This is a list of strings that is the variable names for important kwargs that need to be recreated in networking.
    importantParams =[]

    #If this flag is true and state is set to drawByFeet, then this will be rendered before things without this flag on, so it should appear below other things.
    flatInDrawByFeet = False

    dontSave = False

    circular = False
    radius = 1
    def __init__( self, pos, vel, image=None, group=None, rect=None, animated=None, collidable=None, collideId=None, collideWith=None, mass=None, specialCollision=None, solid=None, pureSensor=None, circular=None, radius=None ):
        pygame.sprite.DirtySprite.__init__( self )
        
        #All of these are purely so that instances CAN have their own unique one of each of these variables, but if one isn't specified, it'll use its Class's one.
        if image is not None:
            self.sheet = image
        if rect is not None:
            self.rect = rect
        if animated is not None:
            self.animated = animated
        if collidable is not None:
            self.collidable = collidable
        if collideId is not None:
            self.collideId = collideId
        if collideWith is not None:
            self.collideWith = collideWith
        if mass is not None:
            self.mass = mass
        #SpecialCollision is a function that defines a unique collision callback for objects with special collision behaviour.
        #Specials happen first, then if the objects are "solid" they have a standard anti-penetration collision too.
        if specialCollision is not None:
            self.specialCollision = specialCollision
        if solid is not None:
            self.solid = solid
        if pureSensor is not None:
            self.pureSensor = pureSensor
        if self.width is None:
            self.width = self.rect.w
        if self.height is None:
            self.height = self.rect.h
        if circular is not None:
            self.circular = circular
        if radius is not None:
            self.radius = radius

        if self.collidable:
            if not self.circular:
                self.body = pymunk.Body( self.mass, 1e100 )
            else:
                self.body = pymunk.Body( self.mass, pymunk.moment_for_circle(self.mass, 0.0, self.radius ) )
            self.body.velocity_limit = 200
            self.body.angular_velocity_limit = 0
            if group.playState.useSuggestedGravityEntityPhysics:
                self.velocity_func = velocityUpdateWrapped
            else:
                self.velocity_func = idleCentricVelocityUpdate
                self.body.velocity_func = idleCentricVelocityUpdate
            if self.ignoreGravity:
                self.body.velocity_func = noGravVelocityUpdate
                self.velocity_func = noGravVelocityUpdate
            
            width, height = self.rect.width, self.rect.height
            self.physicsObjects = [self.body]

            offset = (-float(width)/2, -float(height)/2)

            if self.bHeight is not None and self.bWidth is not None:
                self.sensorBox = pymunk.Poly( self.body, map( pymunk.vec2d.Vec2d, [ (self.bWidth+self.bdx, 0+self.bdy), (self.bWidth+self.bdx, self.bHeight+self.bdy), (0+self.bdx, self.bHeight+self.bdy), (0+self.bdx, 0+self.bdy) ] ), offset )
                self.sensorBox.sensor = True
                self.sensorBox.collision_type = 2
                self.sensorBox.entity = self
                self.sensorId = id( self.sensorBox )
                self.physicsObjects.append( self.sensorBox )

            if not self.circular:
                if self.wbHeight is not None and self.wbWidth is not None:
                    self.shape = pymunk.Poly( self.body, map( pymunk.vec2d.Vec2d, [ (self.wbWidth+self.wbdx, 0+self.wbdy), (self.wbWidth+self.wbdx, self.wbHeight+self.wbdy), (0+self.wbdx, self.wbHeight+self.wbdy), (0+self.wbdx, 0+self.wbdy) ] ), offset )
                elif height is not None and width is not None:
                    self.shape = pymunk.Poly( self.body, map( pymunk.vec2d.Vec2d, [ (width, 0), (width, height), (0, height), (0, 0) ] ), offset )
                else:
                    self.shape = pymunk.Poly( self.body, map( pymunk.vec2d.Vec2d, [ (self.rect.w, 0), (self.rect.w, self.rect.h), (0, self.rect.h), (0, 0) ] ), offset )
    
            else:
                self.shape = pymunk.Circle( self.body, self.radius )

            self.physicsObjects.append( self.shape )
            self.shape.sensor = not self.solid
            self.shape.elasticity = 0.0
            self.shape.friction = 0.5
            self.collision_type = 0
            self.body.position = pymunk.vec2d.Vec2d( pos )
            if self.solid:
                self.shape.collision_type = 1
            else:
                self.shape.collision_type = 2
            self.shape.entity = self
            #group.playState.space.add( self.body, self.shape )
            #self.physicsObjects = [ self.body, self.shape ]

            self.bodyId = id( self.body )
            self.shapeId = id( self.shape )
        else:
            self.rect.topleft = pos[0]+group.playState.panX, pos[1]+group.playState.panY
        
        self.idle = [False, False]
        
        self.animated = animated
        self.animations = {'idle':{ 'fps':8, 'frames':[0] }}
        self.frames = []
        #Copies of all the frames from init time. For stuff like rotatation.
        self.originalFrames = []
        self.curAnimation = self.animations['idle']
        
        self.createFrames()

        self.frame = 0
        self.image = self.frames[0]
        self.maxFrameTime = 1.000/self.curAnimation['fps']
        self.frameTime = self.maxFrameTime

        self.visible = 1
        self.dirty = 2
        
        
        if group != None:
            self.addToGroup( group )
            if group.playState.isHost:
                group.playState.networkNode.addCreateEnt( self )
        else:
            self.id = None
            self.playStateRef = None
        self.tags = {}
        self.children = []
        self.classUpdated = False

        self.oldPan = group.playState.panX, group.playState.panY

        self.angle = 0.0

        if self.collidable:
            framePosition = self.framePositions.get( self.curAnimation['frames'][self.frame], (0,0) )
            self.rect.topleft = self.body.position.x+framePosition[0]+self.oldPan[0], self.body.position.y+framePosition[1]+self.oldPan[1]
            #Behold, a cheap hack to fix circular objects physics and visuals not lining up.
            self.rect.y -= self.height/2
            self.rect.x -= self.width/2

    def addToGroup( self, *groups ):
        self.id = groups[0].playState.idSource.getId()
        self.playStateRef = weakref.ref( groups[0].playState )
        if self.collidable:
            for group in groups:
                group.playState.space.add( self.physicsObjects )
                self.playStateRef = weakref.ref( group.playState )
        pygame.sprite.DirtySprite.add( self, groups )

    def removeFromGroup( self, *groups ):
        self.id = None
        if self.collidable:
            for group in groups:
                group.playState.space.remove( self.physicsObjects )
        pygame.sprite.DirtySprite.remove( self, groups )

    def getPosition( self ):
        if self.collidable:
            return [self.body.position[0], self.body.position[1]]
        else:
            return [self.rect.topleft[0]-self.oldPan[0], self.rect.topleft[1]-self.oldPan[1]]

    def setPosition( self, newPos ):
        self.rect.topleft = newPos[0]+self.oldPan[0], newPos[1]+self.oldPan[1]
        if self.collidable:
            self.body.position.x, self.body.position.y = newPos[0], newPos[1]
            self.rect.y -= self.image.get_height()/2
            self.rect.x -= self.image.get_width()/2

    def createFrames( self ):
        #if self.animated:
        if self.frameRects is None:
            tmpRect = self.rect.copy()
            tmpRect.topleft = ( 0, 0 )
            self.frames = sliceImage( self.sheet, tmpRect, colourKey=self.colourKey )
            if len( self.frames ) is 0:
                self.frames = [self.sheet]
            self.originalFrames = [ each.copy() for each in self.frames ]
        else:
            for eachFrame in self.frameRects:
                img = self.sheet.subsurface( eachFrame )
                img.set_colorkey( self.colourKey )
                self.frames.append( img )
                self.originalFrames = [ each.copy() for each in self.frames ]

    def setRotation( self, angle ):
        #NOTE, angle here is in radians, this needs to be converted for rotozoom which is in degrees.
        deg = math.degrees( angle )
        self.frames = [ pygame.transform.rotozoom( eachFrame.copy(), -deg, 1.0 ) for eachFrame in self.originalFrames ]
        [ each.set_colorkey( self.colourKey ) for each in self.frames ]        
        self.image = self.frames[ self.curAnimation['frames'][self.frame] ]
        if self.collidable:
            self.body.angle = angle
        self.angle = angle
        self.rect = self.image.get_rect().move(self.rect.topleft)

    def setVisible( self, theBool ):
        if theBool:
            self.visible = 1
        else:
            self.visible = 0
        
    def nextFrame( self ):
        self.frame += 1
        if self.frame > len(self.curAnimation['frames']) - 1:
            self.frame = 0
        self.image = self.frames[ self.curAnimation['frames'][self.frame] ]
        self.frameTime = self.maxFrameTime

    def changeAnimation( self, name ):
        newAnim = self.animations[name]
        if self.curAnimation == newAnim:
            return None
        self.curAnimation = newAnim
        self.maxFrameTime = 1.000/self.curAnimation['fps']
        self.frame = -1
        self.nextFrame()
        if self.playStateRef is not None:
            playState =self.playStateRef()
            if playState.isHost:
                playState.networkNode.addChangeAnim( self, name )
        

    #This function changes to a new animation, but keeps the same PERCENTAGE completion of animation, (eg, if one animation playing and is half way through, a swapped in animation will start at halfway )
    def swapAnimation( self, name ):
        curFrameFraction = float(self.frame)/len( self.curAnimation['frames'] )
        #print curFrameFraction
        newAnim = self.animations[name]
        if self.curAnimation == newAnim:
            return None
        self.curAnimation = newAnim
        self.maxFrameTime = 1.000/self.curAnimation['fps']
        self.frame = int( curFrameFraction*len( self.curAnimation['frames'] ) ) - 1
        self.nextFrame()
        if self.playStateRef is not None:
            playState =self.playStateRef()
            if playState.isHost:
                playState.networkNode.addSwapAnim( self, name )
        
    def getMomentumOnAxis( self, axis ):
        return self.mass*self.velocity[axis]

    def changeMaxVel( self, newMax):
        self.maxVel = newMax
        #self.idleDeceleration = self.decelRatio*self.maxVel
    
    def getVelocitySize( self ):
        return ( self.velocity[0]**2 + self.velocity[1]**2 )**0.5
    
    def getNetAccel( self ):
        signX = cmp( self.acceleration[0], 0 )
        signY = cmp( self.acceleration[1], 0 )
        return ( self.acceleration[0] - signX*self.idleDeceleration, self.acceleration[1] - signY*self.idleDeceleration )


    def kill( self ):
        playState = self.playStateRef()
        if self.collidable:
            playState.space.remove( self.physicsObjects )
        if playState.isHost:
            playState.networkNode.addRemoveEnt( self )
        pygame.sprite.DirtySprite.kill( self )
        

    def update( self, dt ):
        if self.animated:
            self.frameTime -= dt
            if self.frameTime <= 0:
                self.nextFrame()
        
        self.rect.x -= self.oldPan[0]
        self.rect.y -= self.oldPan[1]

        if self.collidable:
            framePositionVector = pymunk.vec2d.Vec2d(self.framePositions.get( self.curAnimation['frames'][self.frame], (0,0) ))
            framePositionVector.rotate(self.angle)
            framePosition = framePositionVector.int_tuple
            self.rect.topleft = self.body.position.x+framePosition[0], self.body.position.y+framePosition[1]
            self.rect.y -= self.image.get_height()/2
            self.rect.x -= self.image.get_width()/2

        listOfGroups = self.groups()
        if len( listOfGroups ) > 0:
            npx = self.playStateRef().panX
            npy = self.playStateRef().panY
        else:
            npx, npy = 0, 0
        self.rect.x += npx
        self.rect.y += npy

        self.oldPan = npx, npy

        #else:
        #    self.rect.topleft = int( round( self.position[0] ) ), int( round( self.position[1] ) )
#        #Assume idle at end of frame
        self.idle = [True, True]

        #Check if class has been updated.
        if self.classUpdated:
            self.frames = []

            self.rect.w = self.width
            self.rect.h = self.height
            

            self.createFrames()
            self.classUpdated = False

        if len( self.groups() ) > 1:
            raise Exception( "An instance of Entity is in more than one group, that should probably not be happening." )

        self.pushed = [0, 0]
