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

import extern_modules.pygnetic as pygnetic, networkhandlers, weakref

class NetworkClient( pygnetic.Client ):
	def __init__( self, playState, conn_limit=1, *args, **kwargs ):
		pygnetic.Client.__init__( self, conn_limit, *args, **kwargs )
		
		self.playStateRef = weakref.ref( playState )

		self.networkTick = None

	def connect( self, address, port, message_factory=pygnetic.message.message_factory, **kwargs ):
		connection = pygnetic.Client.connect( address, port, message_factory, **kwargs )
		connection.add_handler( networkhandlers.ClientHandler( self ) )
