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

from collections import namedtuple

#This object describes the event of an entity being created
CreateEnt = namedtuple( 'CreateEnt', ['entId', 'className', 'position', 'velocity', 'kwargs'] )

#This object describes the event of removing an ent.
RemoveEnt = namedtuple( 'RemoveEnt', ['entId'] )

#This object describes the event of an Entities location updating.
UpdatePosition = namedtuple( 'UpdatePosition', ['entId', 'newPosition'] )

#This object describes the event of a sound starting.
StartSound = namedtuple( 'StartSound', ['soundName', 'priority', 'loops', 'maxtime', 'fade_ms'] )

#This object describe the event of a sound ending.
StopSound = namedtuple( 'StopSound', ['stopId', 'soundName'] )

#This object describes the event of an ent swapping animation.
SwapAnim = namedtuple( 'SwapAnim', ['entId', 'newAnimName'] )

#This object describe the event of an ent changing animation.
ChangeAnim = namedtuple( 'ChangeAnim', ['entId', 'newAnimName'] )
