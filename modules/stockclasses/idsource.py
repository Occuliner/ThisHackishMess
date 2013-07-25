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

"""This is an IdSource, all it does is hand out integers, starting at zero, it never resets in it's life. The reason this isn't just a variable that's incremented is to forget accidentally not incrementing and avoiding outside tampering."""

class IdSource( object ):
    def __init__( self ):
        self.__dict__["_currentNumber"] = 0

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

