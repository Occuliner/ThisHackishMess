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

import extern_modules.pygnetic as pygnetic, networkmessages, weakref

class ClientHandler(pygnetic.Handler):
	def __init__( self, playState ):
		self.playStateRef = weakref.ref( playState )
	def net_joinLobby( self, message, **kwargs ):
		pass
	def net_joinGame( self, message, **kwargs ):
		pass
	def net_acceptPlayer( self, message, **kwargs ):
		pass
	def net_kickPlayer( self, message, **kwargs ):
		pass
	def net_chatToClient( self, message, **kwargs ):
		pass
	def net_chatToHost( self, message, **kwargs ):
		pass
	def net_createEnt( self, message, **kwargs ):
		pass
	def net_removeEnt( self, message, **kwargs ):
		pass
	def net_entityPositionUpdate( self, message, **kwargs ):
		pass
	def net_changeAnim( self, message, **kwargs ):
		pass
	def net_swapAnim( self, message, **kwargs ):
		pass
	def net_loadSound( self, message, **kwargs ):
		pass
	def net_playSound( self, message, **kwargs ):
		pass
	def net_stopSound( self, message, **kwargs ):
		pass

class ServerHandler(pygnetic.Handler):
	def __init__( self, playState ):
		self.playStateRef = weakref.ref( playState )
	def net_joinLobby( self, message, **kwargs ):
		pass
	def net_joinGame( self, message, **kwargs ):
		pass
	def net_acceptPlayer( self, message, **kwargs ):
		pass
	def net_kickPlayer( self, message, **kwargs ):
		pass
	def net_chatToClient( self, message, **kwargs ):
		pass
	def net_chatToHost( self, message, **kwargs ):
		pass
	def net_createEnt( self, message, **kwargs ):
		pass
	def net_removeEnt( self, message, **kwargs ):
		pass
	def net_entityPositionUpdate( self, message, **kwargs ):
		pass
	def net_changeAnim( self, message, **kwargs ):
		pass
	def net_swapAnim( self, message, **kwargs ):
		pass
	def net_loadSound( self, message, **kwargs ):
		pass
	def net_playSound( self, message, **kwargs ):
		pass
	def net_stopSound( self, message, **kwargs ):
		pass

