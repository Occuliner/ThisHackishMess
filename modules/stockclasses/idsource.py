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

"""This is an IdSource, all it does is hand out integers, starting at zero, it never resets in it's life. The reason this isn't just a variable that's incremented is to forget accidentally not incrementing and avoiding outside tampering."""

class IdSource( object ):
	def __init__( self ):
		self._currentNumber = 0

	def __setattr__( self, name, value ):
		if name == "_currentNumber":
			raise Exception( "NO. NO. You are NOT supposed to reference IdSources _currentNumber. Just no." )
		else:
			self.__dict__[name] = value

	def __getattribute__( self, name ):
		if name == "_currentNumber":
			raise Exception( "NO. NO. You are NOT supposed to reference IdSources _currentNumber. Just no." )
		else:
			return object.__getattribute__( self, name )

	def getId( self ):
		self.__dict__["_currentNumber"] += 1
		return self.__dict__["_currentNumber"] - 1

