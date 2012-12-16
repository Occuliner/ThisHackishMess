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

import extern_modules.pygnetic as pygnetic

#pygnetic.init( logging_lvl=None )

#Register all the messages types in this file, to make sure they're in the correct order for both client and host.

def registerMessages():
	#This message is sent when the host doesn't instant-kick the client, it also contains the current level name.
	pygnetic.register( 'requestInfo', ('soundMgrCurPlayId', 'levelName') )

	#This message is sent on info request
	pygnetic.register( 'hereIsMyInfo', ('name') )

	#This message is sent when the player hits join game.
	pygnetic.register( 'joinGame', ('name') )

	#This message is sent when the host accepts the joinGame request.
	pygnetic.register( 'acceptPlayer', ('name') )

	#This message is sent when the host kicks a player.
	pygnetic.register( 'kickPlayer', ('duration', 'reason') )

	#This message is sent from the host to the player containing messages from other players.
	pygnetic.register( 'chatToClient', ('name', 'message') )

	#This message is sent from the player to the host when they say a message, the groupId paramter is for team say, the server can use the id to determine which players get the message.
	pygnetic.register( 'chatToHost', ( 'message', 'groupId' ) )

	#This message is sent from the host to the player every tick. Each parameter is a list of objects that describe some event that happened this tick.
	pygnetic.register( 'updateEvent', ('tickNum', 'createEnts', 'removeEnts', 'updatePositions', 'startSounds', 'stopSounds', 'changeAnims', 'swapAnims') )

	#This message is sent from the player to the host containing the players input dicts.
	pygnetic.register( 'inputEvent', ('tickNum', 'inputDict') )

	#This message is sent from the client to the host to get ping, the host then echos it.
	pygnetic.register( 'clientRequestPing', ('timeStamp') )

	#This message is sent from the host to the client to get ping, the client then echos it.
	pygnetic.register( 'hostRquestPing', ('timeStamp') )

	#This message is sent from the host to the client to force a list of ents to have certain frames.
	pygnetic.register( 'forceEntFrame', ('tickNum', 'entIdFrameTuples') )

	#This message is sent from the host to the client to force a bunch of sounds into mid-play.
	pygnetic.register( 'forcePlayingSound', ('tickNum', 'soundTuples') )

	#This message is sent from the host to client to force a set of velocities. This could be put into the updateEvent tuple, but I don't want to need it to be modified between making a game use extrapolation or interpolation.
	pygnetic.register( 'forceVelocities', ('tickNum', 'entIdVelocityTuples') )

###Merge these all into a single event, each being a sub-event. This is to make sure you receive whole updates. There is no interest in partial updates.
##This message is to create a network ent on the client side.
#pygnetic.register( 'createEnt', ('className', 'id', 'animation', 'frameNum') )
#
##This message is sent to remove a network ent.
#pygnetic.register( 'removeEnt', ('id') )
#
##This message is sent to update object locations,
#pygnetic.register( 'entityPositionUpdate', ('id', 'newPosition') )
#
##This message is to send that a certain entity is changing animation.
#pygnetic.register( 'changeAnim', ('id', 'newAnimation') )
#
##This message is to send that a certain entity is swapping animation.
#pygnetic.register( 'swapAnim', ('id', 'newAnimation') )
#
##This message is sent to play a certain sound.
#pygnetic.register( 'playSound', ('soundname' ) )
#
##This message is sent to stop a certain sound.
#pygnetic.register( 'stopSound', ('soundname') )
