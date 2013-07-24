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

"""This file defines the MenuState class."""

from label import Label
from minimap import MiniMap
from getres import getResolution

class MenuState:
    """The MenuState class. Generally serves two purposes:\n""" \
    """-Contains Buttons to be displayed and potentially clicked on.\n""" \
    """-Contains an update method, that is called when the user clicks \n""" \
    """    outside the menu, whilst the menu is open."""
    def __init__( self, menu, sprites=[], miniMap=True ):
        self.sprites = sprites
        self.buttons = []
        self.menu = menu
        for eachSprite in self.sprites:
            if eachSprite.button:
                self.buttons.append( eachSprite )
            eachSprite.parentState = self
                #eachSprite.menu = menu
        self.keyInput = ""
        self.keyboardEnabled = False
        self.x, self.y = 0, 0
        self.fileNameLabel = Label( self, menu.playState.fileName, (0,getResolution()[1]-32) )
        self.addSprite( self.fileNameLabel )
        self.usingMiniMap = miniMap
        if miniMap:
            self.addMiniMap()
        self.miniMapFlip = False

    def addMiniMap( self ):
        self.miniMap = MiniMap( self, 160, 120 )
        self.addSprite( self.miniMap )

    def moveTo( self, x, y ):
        w, h = getResolution()
        if x-self.x+self.panel.rect.left < 0:
            x -= x-self.x+self.panel.rect.left
        elif x-self.x+self.panel.rect.right > w:
            x -= x-self.x+self.panel.rect.right-w
        if y-self.y+self.panel.rect.top < 0:
            y -= y-self.y+self.panel.rect.top
        elif y-self.y+self.panel.rect.bottom > h:
            y -= y-self.y+self.panel.rect.bottom-h
        dx, dy = x-self.x,y-self.y
        self.x, self.y = x, y
        for each in [ sprite for sprite in self.sprites if not sprite.fixed ]:
            each.rect.topleft = each.rect.x+dx, each.rect.y+dy

    def addButton( self, button, spriteIndex=None ):
        """Adds a button to the MenuState."""
        #button.parentState = self
        #self.sprites.append( button )
        self.addSprite( button, spriteIndex )    
        self.buttons.append( button )

    def addSprite( self, sprite, index=None ):
        """Adds a sprite to the MenuState."""
        sprite.parentState = self
        if not sprite.fixed:
            sprite.rect.x += self.x
            sprite.rect.y += self.y
        if index is None or index > len( self.sprites ) - 1:
            self.sprites.append( sprite )
        else:
            self.sprites.insert( index, sprite )

    def removeSprite( self, sprite ):
        self.sprites.remove( sprite )
        if not sprite.fixed:
            sprite.rect.x -= self.x
            sprite.rect.y -= self.y
        
    def removeButton( self, button ):
        self.removeSprite( button )
        self.buttons.remove( button )

    def update( self, dt, clickPoint, clickKey, curMousePos ):
        """The method that runs when the user has clicked somewhere outside of the menu,\n""" \
        """whilst the menu is still open."""
        if self.usingMiniMap:
            self.miniMapFlip = not self.miniMapFlip
            if self.miniMapFlip:
                self.miniMap.regenerateImage()
            if self.miniMap.held:
                if self.miniMap.dragging:
                    self.miniMap.rect.topleft = curMousePos[0]-self.miniMap.heldPos[0], curMousePos[1]-self.miniMap.heldPos[1]
                    MiniMap.pos = self.miniMap.rect.topleft
                if self.miniMap.panning:
                    self.miniMap.pan( curMousePos )
                if not self.miniMap.rect.collidepoint( curMousePos ):
                    self.miniMap.held = False
                    self.miniMap.heldPos = None
                    self.miniMap.dragging = False
                    self.miniMap.panning = False

    def keyboardInput( self, keyEvent ):
        self.keyInput += keyEvent

    def getKeyboardInput( self ):
        result = self.keyInput
        self.keyInput = ""
        return result

