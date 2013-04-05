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

from imageload import loadImage

from button import Button

import pygame

class PauseStartButton( Button ):
    image = loadImage("pausestart.png",2)
    def __init__( self, menu=None ):
        Button.__init__( self, None, None, menu )
        self.rect = self.image.get_rect()
        self.rect.topleft = ( 60, 370 )
        self.on = False
    def push( self, clickKey, click ):
        if "up" in clickKey:
            if not self.on:
                self.on = True
            elif self.on:
                self.on = False
            self.parentState.menu.playState.paused = self.on
            if self.on:
                pygame.mixer.pause()
            else:
                pygame.mixer.unpause()
