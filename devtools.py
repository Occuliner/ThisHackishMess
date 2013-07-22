#    Copyright (c) 2012 Connor Sherson
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
    
    def __init__( self,  gamePlayState, ):
        pygame.sprite.OrderedUpdates.__init__( self )

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

        self.masterEntSet = MasterEntitySet()

        self.defaultMenuState = DefaultMenuState( self )

        self.loadMenuState( self.defaultMenuState )

        #FUCKING HORRIBLE HIDEOUS HACK OH GOD WHY.
        #Foricbly reload everything in EntitySets so that they're actually added 
        #to the MasterEntSet, I should really find someway of doing this right
        #the first time.
	self.theModuleLoader.loadModules( os.path.join( "modules", "entitysets" ) )
        self.masterEntSet.updateEnts()

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
                #if curButtonArea.collidepoint( eachClick ):
                #    someButtonPressed = False
                #    for eachButton in self.buttons:
                #        if eachButton.rect.collidepoint( eachClick ):
                #            eachButton.push( clickKey )
                #            someButtonPressed = True
                #            break
                #    if not someButtonPressed and "down" in clickKey:
                #        self.draggingMenu = True
                #        self.draggedSpot = curMousePos[0]-self.menuState.x, curMousePos[1]-self.menuState.y
                #else:
                #    self.menuState.update( dt, eachClick, clickKey, curMousePos )
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
            map(lambda eachSprite:classUpdateInPlace(eachSprite, globals(), locals()), self.playState.sprites())

            self.playState.floor.tileSet.updateSets()
            self.masterEntSet.updateEnts()
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
                changedAreas.append( pygame.Rect( 0 , 0, 800, 600 ) )
            return changedAreas
        elif self.wasOpen:
            self.wasOpen = False
            #return [ self.devPanel.rect ]
            return [ pygame.Rect( 0, 0, 800, 600 ) ]    
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
