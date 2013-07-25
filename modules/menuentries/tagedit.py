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

import pygame, os

from imageload import loadImage

from button import Button

from menustate import MenuState

from staticimage import StaticImage

from label import Label

class TagEditButton( Button ):
    image = loadImage( "tageditbutton.png", 2 )
    rect = image.get_rect()
    rect.topleft = ( 24, 104 )
    def __init__( self, menu=None ):
        Button.__init__( self, None, None, menu )

    def push( self, clickKey, click ):
        if "up" in clickKey:
            aTagEditState = TagEditState( self.parentState.menu )
            self.parentState.menu.loadMenuState( aTagEditState )

def dictToStrings( givenDict ):
    return [ str(eachKey)+":"+str(eachVal) for eachKey, eachVal in givenDict.items() ]
        
class TagButton( Button ):
    TagButtonText = pygame.font.Font( os.path.join( "data", "fonts", "PD-tarzeau_-_Atari_Small.ttf" ), 16 )
    def __init__( self, parentState=None, text="", pos=(0,0) ):
        Button.__init__( self, None, None, parentState )
        self.text = text
        self.rect = pygame.Rect( 0, 0, 0, 0 ).move( pos[0], pos[1] )
        #print text
        self.selected = False
        self.createText()

    

    def renderImage( self ):
        if self.selected:
            self.background.fill( pygame.Color( 255, 0, 0 ) )
            self.image.blit( self.background, (0, 0) )
            self.image.blit( self.textImage, (0, 0) )
        else:
            self.image = self.textImage.copy().convert(32)
        
        
    def createText( self ):
        oldX, oldY = self.rect.topleft
        self.textImage = self.TagButtonText.render( self.text, False, pygame.Color( 0, 0, 0 ) )
        damnRect = self.textImage.get_rect()
        self.background = pygame.Surface( ( damnRect.w, damnRect.h ), depth=32 )
        self.image = pygame.Surface( ( damnRect.w, damnRect.h ) )
        self.renderImage()
        self.rect = damnRect
        self.rect.topleft = oldX, oldY

    def getKeyValuePair( self ):
        return self.text.rsplit( ":", 1 )

    def toggleSelect( self ):
        if self.selected:
            self.parentState.curTag = None
            self.selected = False
            self.renderImage()
            self.parentState.curEnt.tags = self.parentState.getDictionaryFromTags()
        else:
            self.parentState.curTag = self
            self.selected = True
            self.renderImage()

    def push( self, clickKey, click ):
        if "up" in clickKey:
            if self.parentState.curTag is not self and self.parentState.curTag is not None:
                self.parentState.curTag.toggleSelect()
            self.toggleSelect()

class AddTagButton( Button ):
    image = loadImage( "add.png", 2 )
    def __init__( self, parentState=None ):
        Button.__init__( self, None, None, parentState )
        self.rect = self.image.get_rect()
        self.rect.topleft = ( 30, 370 )
    def push( self, clickKey, click ):
        if "up" in clickKey:
            curEnt = self.parentState.curEnt
            if curEnt is not None:
                num = len( curEnt.tags )+1
                done = False
                while not done:
                    if str(num) not in curEnt.tags.keys():
                        done = True
                    else:
                        num += 1
                curEnt.tags[str(num)] = ""
                self.parentState.getTagButtons()

class SubTagButton( Button ):
    image = loadImage( "sub.png", 2 )
    def __init__( self, parentState=None ):
        Button.__init__( self, None, None, parentState )
        self.rect = self.image.get_rect()
        self.rect.topleft = ( 60, 370 )
    def push( self, clickKey, click ):
        if "up" in clickKey:
            curEnt = self.parentState.curEnt
            if curEnt is not None:
                curTag = self.parentState.curTag
                if curTag is not None:
                    del curEnt.tags[curTag.getKeyValuePair()[0]]
                    self.parentState.getTagButtons()

#
class TagEditState( MenuState ):
    def __init__( self, menu, sprites=[] ):
        MenuState.__init__( self, menu, sprites )
        self.sprites = [self.fileNameLabel, self.miniMap]
        self.buttons = []

        self.panel = StaticImage( loadImage( "tageditorbackground.png", 2 ), (10, 10) )
        self.addSprite( self.panel )
        self.plusTagButton = AddTagButton( self )
        self.addButton( self.plusTagButton )
        self.subTagButton = SubTagButton( self )
        self.addButton( self.subTagButton )

        self.curEnt = None

        self.keyboardEnabled = True
        #self.currentString = ""
        self.deleteLastChar = False
        #self.oldString = ""

        self.curTag = None
        self.tagButtons = []

        self.carryMeOverButtons = [self.plusTagButton, self.subTagButton]
        self.carryMeOverSprites = [self.panel,self.fileNameLabel] + self.carryMeOverButtons

    def addButton( self, givenButton ):
        MenuState.addButton( self, givenButton )
        if givenButton.__class__.__name__ == "TagButton":
            self.tagButtons.append( givenButton )
    
    def getTagButtons( self ):
        self.tagButtons, self.buttons, self.sprites = [], list( self.carryMeOverButtons ), list( self.carryMeOverSprites )
        self.curTag = None
        if self.curEnt is None:
            return None
        tagStrings = dictToStrings( self.curEnt.tags )
        curX, curY = 21, 30
        for eachString in tagStrings:
            eachButton = TagButton( self, eachString, ( curX, curY ) )
            curY += eachButton.rect.h
            self.addButton( eachButton )
        self.menu.loadMenuState( self )

    def getPressedEnt( self, point ):
        """See which ent is at this point"""
        for eachSpriteList in ( eachGroup.sprites() for eachGroup in self.menu.playState.groups ):
            for eachSprite in eachSpriteList:
                if eachSprite.bWidth is not None:
                    start = eachSprite.rect.topleft
                    givenRect = pygame.Rect( (start[0] + eachSprite.bdx, start[1] + eachSprite.bdy), (eachSprite.bWidth, eachSprite.bHeight) )
                else:
                    givenRect = eachSprite.rect
                if givenRect.collidepoint( point ):
                    return eachSprite

    def getDictionaryFromTags( self ):
        return dict( [ eachTag.getKeyValuePair() for eachTag in self.tagButtons ] )
        

    def update( self, dt, click, clickKey, curMousePos=None ):
        MenuState.update( self, dt, click, clickKey, curMousePos )
        if click is not None:
            if clickKey is 'mouse1down':
                self.curEnt = self.getPressedEnt( curMousePos )
                self.getTagButtons()
        if self.curTag is not None:
            oldText = self.curTag.text
            if self.deleteLastChar:
                self.curTag.text =  self.curTag.text[:-1]
                self.deleteLastChar = False
            self.curTag.text += self.getKeyboardInput()
            if self.curTag.text != oldText:
                self.curTag.createText()
        else:
            #if self.curEnt is not None:
            #    self.curEnt.tags = self.getDictionaryFromTags()
            #Clear keyboard input if no tag selected.
            self.getKeyboardInput()
