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

"""The devtools file defines the DevMenu class."""
import pygame, weakref, os

from imageload import loadImage

from moduleloader import ModuleLoader
        
class DevMenu( pygame.sprite.OrderedUpdates ):
    """
    DevMenu()

    The DevMenu class is the base-class for the developer menu.
    Contains buttons on the menu, a menu state, a reference to 
    the playState. Ultimately it is a middle-section between the 
    main-loop and the various menu states."""
    
    def __init__( self,  gamePlayState, devMode ):
        pygame.sprite.OrderedUpdates.__init__( self )

        self.devMode = devMode

        self.theModuleLoader = ModuleLoader(globals(), locals())
        self.theModuleLoader.loadModules("modules")

        self.reloadTime = 1.000
        self.curTimeTillReload = self.reloadTime
        
        #self.devPanel = StaticImage(loadImage("devmenu.png"), (10, 10))    
        #self.add(self.devPanel)
        self.open = False

        self.rerenderEverythingIn = -1
        
        #This boolean is set to true after the menu is closed. 
        #It is used by draw() to tell when the menu was open last frame, 
        #so that it can return an update rect that covers the whole devmenu. 
        #So it may be cleared.
        self.wasOpen = False

        #This list will contain click events that are
        # added to it during the main.py main loop.
        #It is processed when DevMenu.update() is called
        self.clicks = {'mouse1up':[], 'mouse1down':[], 'mouse2up':[], 'mouse2down':[], 'mouse3up':[], 'mouse3down':[]}

        #All the sprites that are also buttons.
        self.buttons = []

        self.playState = gamePlayState

        self.masterEntitySet = MasterEntitySet()
        #If in devMode, force load every damn ent.
        if self.devMode:
            self.masterEntitySet.loadAllEnts()

        self.defaultMenuState = DefaultMenuState( self )

        self.loadMenuState( self.defaultMenuState )

        #FUCKING HORRIBLE HIDEOUS HACK OH GOD WHY.
        #Foricbly reload everything in EntitySets so that they're actually added 
        #to the MasterEntSet, I should really find someway of doing this right
        #the first time.
	#self.theModuleLoader.loadModules( os.path.join( "modules", "entitysets" ) )
        #self.masterEntSet.updateEnts()

        self.draggingMenu = False
        self.draggedSpot = [0,0]

        self.playState.devMenuRef = weakref.ref( self )
        
    def toggle( self ):
        """Flips the DevMenu.open boolean, and wasOpen boolean.
        (Also forces the DevMenu into the defaultMenuState)"""
        self.open = not self.open
        self.wasOpen = not self.open
        #self.loadMenuState( self.defaultMenuState )
        self.backToDefault()

    def backToDefault( self ):
        self.defaultMenuState.removeSprite( self.defaultMenuState.fileNameLabel )
        self.defaultMenuState.fileNameLabel = Label( self, self.playState.fileName, (0,570) )
        self.defaultMenuState.addSprite( self.defaultMenuState.fileNameLabel )
        self.loadMenuState( self.defaultMenuState )
        
    
    def update( self, dt ):
        """Generic update function.
        Checks for button clicks. Sends other clicks to the MenuState.
        Forces a reload of all the modules, and class redefintions to 
        the MenuState, PlayState, each sprite in the playState and all
        of the buttons in the DevMenu."""
        
        if not self.open:
            return False
        
        curMousePos = pygame.mouse.get_pos()
        
        self.menuState.update( dt, None, None, curMousePos )
        curButtonArea = self.menuState.panel.rect
        for clickKey, clickList in self.clicks.items():
            for eachClick in clickList:
                someButtonPressed = False
                for eachButton in self.buttons:
                    if eachButton.rect.collidepoint( eachClick ):
                        eachButton.push( clickKey, eachClick )
                        someButtonPressed = True
                        break
                if not someButtonPressed:
                    if curButtonArea.collidepoint( eachClick ):
                        if "down" in clickKey:
                            self.draggingMenu = True
                            self.draggedSpot = curMousePos[0]-self.menuState.x, curMousePos[1]-self.menuState.y
                    else:
                        self.menuState.update( 0, eachClick, clickKey, curMousePos )
                self.clicks[clickKey].remove( eachClick )
            
        if self.draggingMenu:
            self.menuState.moveTo( curMousePos[0]-self.draggedSpot[0], curMousePos[1]-self.draggedSpot[1] )

        for each in iter( self ):
            each.update( self, dt )

        self.curTimeTillReload -= dt
        if self.curTimeTillReload <= 0.000:
            self.theModuleLoader.loadModules( "modules" )
            self.curTimeTillReload = self.reloadTime

            #This might cause issues because globals() and locals() 
            #is only called once. But I am going to assume it won't.
            map(lambda eachSprite:classUpdateInPlace(eachSprite, globals(), locals()), self.sprites())
            
            classUpdateInPlace( self.menuState, globals(), locals() )

            #classUpdateInPlace( self.playState, globals(), locals() )

            #ISOLATED CODE 1
            #map(lambda eachSprite:classUpdateInPlace(eachSprite, globals(), locals()), self.playState.sprites())

            self.playState.floor.tileSet.updateSets()
        if self.playState.forceUpdateEverything:
            map(lambda eachSprite:classUpdateInPlace(eachSprite, globals(), locals()), self.sprites())
            #classUpdateInPlace( self.playState, globals(), locals() )
            self.playState.forceUpdateEverything = False
        return True
        #print dt

    def draw( self, surface ):
        """Draws everything the DevMenu, returns a list of of screen areas changed by
        Menu-rendering, but also from changes to the playState's floor."""
        if self.open:
            changedAreas = []
            changedAreas.extend( pygame.sprite.OrderedUpdates.draw( self, surface ) )
            changedAreas.extend( self.playState.floor.popChangedAreas() )
            if self.rerenderEverythingIn > 0:
                self.rerenderEverythingIn -= 1
            elif self.rerenderEverythingIn == 0:
                self.rerenderEverythingIn -= 1
                changedAreas.append( pygame.Rect( 0 , 0, surface.get_width(), surface.get_height() ) )
            return changedAreas
        elif self.wasOpen:
            self.wasOpen = False
            return [ pygame.Rect( 0, 0, surface.get_width(), surface.get_height() ) ]    
        else:
            return []
    
    #THIS remove() function doesn't support unlimited sprite args, unfortunately.
    def remove( self, *sprites ):
        """Removes sprites (See buttons) from the DevMenu"""
        pygame.sprite.OrderedUpdates.remove( self, *sprites )
        for sprite in sprites:
            if sprite.button:
                self.buttons.remove( sprite )

    #Neither does this add()
    def add( self, *sprites ):
        """Adds sprites (See buttons) to the DevMenu"""
        pygame.sprite.OrderedUpdates.add( self, *sprites )
        for sprite in sprites:
            if sprite.button:
                self.buttons.append( sprite )

    def loadMenuState( self, newMenuState ):
        """Loads a new MenuState, for the DevMenu and swaps in the new buttons."""
        if hasattr( self, "menuState" ):
            curX, curY = self.menuState.x, self.menuState.y
        else:
            curX, curY = 0, 0
        self.empty()
        self.buttons = []
        #self.add( self.devPanel )
        if hasattr( self, 'menuState' ):
            del self.menuState
        map( self.add, newMenuState.sprites )
        self.menuState = newMenuState
        self.menuState.moveTo( curX, curY )
