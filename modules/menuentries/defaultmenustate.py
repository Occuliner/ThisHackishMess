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

"""This file defines the DefaultMenuState Class.\n""" \
"""It is a type of MenuState for the DevMenu, can you guess which one?"""

from menustate import MenuState

from flooredit import FloorEditButton

from entityedit import EntityEditButton

from loadmap import LoadMapButton

from savemap import SaveMapButton

from tagedit import TagEditButton

from boundaryedit import BoundaryEditButton

from sensoredit import SensorEditButton

from physicsvis import PhysicsVisButton

from staticimage import StaticImage

from imageload import loadImage

from label import Label

class DefaultMenuState( MenuState ):
	"""The DefaultMenuState is the class for the default MenuState.\n""" \
	"""Shocking, I know."""
	floorEditButton = FloorEditButton()

	entityEditButton = EntityEditButton()

	saveMapButton = SaveMapButton()

	loadMapButton = LoadMapButton()

	tagEditButton = TagEditButton()

	boundEditButton = BoundaryEditButton()

	physicsVisButton = PhysicsVisButton()

	sensorEditButton = SensorEditButton ()

	panel = StaticImage( loadImage("devmenu.png", 2), (10, 10) )

	def __init__( self, menu, sprites=[panel, floorEditButton, entityEditButton, saveMapButton, loadMapButton, tagEditButton, boundEditButton, physicsVisButton, sensorEditButton] ):
		MenuState.__init__( self, menu, sprites )
