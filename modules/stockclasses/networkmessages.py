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

import extern_modules.pygnetic as pygnetic

#pygnetic.init( logging_lvl=None )

#Register all the messages types in this file, to make sure they're in the correct order for both client and host.

def registerMessages():
    #This message is sent when the host doesn't instant-kick the client, it also contains the current level name.
    pygnetic.register( 'requestInfo', ('time') )

    #This message is sent on info request
    pygnetic.register( 'hereIsMyInfo', ('time', 'name') )

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
    pygnetic.register( 'updateEvent', ('tickNum', 'time', 'clientTime', 'clientLastAckTime', 'clientInputCount', 'createEnts', 'removeEnts', 'updatePositions', 'vels', 'startSounds', 'stopSounds', 'changeAnims', 'swapAnims') )

    #This message is sent from the host to the player every tick. Each parameter is a list of objects that describe some event that happened this tick.
    pygnetic.register( 'createEvent', ('tickNum', 'time', 'clientTime', 'clientLastAckTime', 'clientInputCount', 'createEnts', 'removeEnts', 'updatePositions', 'vels', 'startSounds', 'stopSounds','changeAnims', 'swapAnims') )

    #This message is sent from the player to the host containing the players input dicts.
    pygnetic.register( 'inputEvent', ('tickNum', 'time', 'inputDict') )

    #This message is sent from the client to the host to get ping, the host then echos it.
    pygnetic.register( 'clientRequestPing', ('timeStamp') )

    #This message is sent from the host to the client to get ping, the client then echos it.
    pygnetic.register( 'hostRquestPing', ('timeStamp') )

    #This message is sent from the host to the client to force a list of ents to have certain frames.
    pygnetic.register( 'forceEntFrame', ('tickNum', 'entIdFrameTuples') )

    #This message is sent from the host to the client to force a bunch of sounds into mid-play.
    pygnetic.register( 'forcePlayingSound', ('tickNum', 'soundTuples') )

    #This message is sent from the host to client to force a set of velocities. This could be put into the updateEvent tuple, but I don't want to need it to be modified between making a game use extrapolation or interpolation.
    pygnetic.register( 'forceVelocities', ('tickNum', 'time', 'clientTime', 'entIdVelocityTuples') )

    #This message is sent from the client to the host to enforce player data.
    pygnetic.register( 'playerUpdate', ('tickNum', 'serverTime', 'id', 'loc', 'vel') )

    #This message is sent from the host to the client to tell the client that a given ent should be added to it's local players group.
    pygnetic.register( 'setPlayerEnt', ('tickNum', 'id') )

    #This message is sent from the host to the client to tell the client to perform GameLogicManager call.
    pygnetic.register( 'gameLogicCall', ('tickNum', 'methodName', 'callArgs', 'callKwargs') )

    #This message is sent from the client to the host to call a GLM method, with easy checking to stop people calling ones they're not allowed to.
    pygnetic.register( 'clientGameLogicCall', ('tickNum', 'methodName', 'argDict') )

    #This message is sent from the host to the client, its a damn map.
    pygnetic.register( 'sendMapBuffer', ('tickNum', 'mapName', 'mapBuffer') )

    #This message is sent from the host to the client to request a map download.
    pygnetic.register( 'requsetMapBuffer', ('tickNum', 'mapName') )

    #This message is sent from the client to the host on player death.
    pygnetic.register( 'playerIsDead', ('tickNum', 'entId') )

    #This message is sent from host to the client on map load.
    pygnetic.register( 'loadMap', ('tickNum', 'levelName', 'soundMgrCurPlayId') )

    #This message is sent from the client to the host to request the info needed to recreate the the scene as it is at this point.
    pygnetic.register( 'requestState', ('tickNum') )

    #This message is sent from the client to the host to request a new loadMap message.
    pygnetic.register( 'requestLoadMap', ('tickNum') )

    #This message is sent from the client to the host so the host can know it can start sending regular updates to the client.
    pygnetic.register( 'everythingIsSet', ('tickNum') )

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
