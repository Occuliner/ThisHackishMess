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

from collections import namedtuple

#This object describes the event of an entity being created
CreateEnt = namedtuple( 'CreatedEnt', ['entId', 'className', 'position', 'velocity'] )

#This object describes the event of removing an ent.
RemoveEnt = namedtuple( 'RemoveEnt', ['entId'] )

#This object describes the event of an Entities location updating.
UpdatePosition = namedtuple( 'UpdatePosition', ['entId', 'newPosition'] )

#This object describes the event of a sound starting.
StartSound = namedtuple( 'StartSound', ['soundName', 'loops'] )

#This object describe the event of a sound ending.
StopSound = namedtuple( 'StopSound', ['stopId'] )

#This object describes the event of an ent swapping animation.
SwapAnim = namedtuple( 'SwapAnim', ['entId', 'newAnimName'] )

#This object describe the event of an ent changing animation.
ChangeAnim = namedtuple( 'ChangeAnim', ['entId', 'newAnimName'] )
