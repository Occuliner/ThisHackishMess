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

from random import randint

def momentumCollideRects( object1, object2, clippedArea, dt ):
	if clippedArea.width < clippedArea.height:
		#print "yay"
		sign = -1*cmp( object1.position[0], object2.position[0] )
		
		#Normal force for all materials
		#object1.acceleration[0] += -object1.idleDeceleration*sign*2.0*clippedArea.width
		#object2.acceleration[0] += object2.idleDeceleration*sign*2.0*clippedArea.width
		
		if ( object1.velocity[0]*sign > 0 and object1.velocity[0]*sign > object2.velocity[0]*sign ) or ( object2.velocity[0]*sign < 0 and object2.velocity[0]*sign < object1.velocity[0]*sign ):
			#obj1NewVel = float( (object1.velocity[0]*(object1.mass-object2.mass)+2*object2.mass*object2.velocity[0]) )/(object1.mass+object2.mass)
			#obj2NewVel = float( (object2.velocity[0]*(object2.mass-object1.mass)+2*object1.mass*object1.velocity[0]) )/(object1.mass+object2.mass)
			obj1NewVel = float( ( (object1.velocity[0]*object1.mass) + (object2.velocity[0]*object2.mass) ) )/(object1.mass+object2.mass)
			obj2NewVel = obj1NewVel
			object1.velocity[0] = obj1NewVel
			object2.velocity[0] = obj2NewVel
			#object1.acceleration[0] += float(obj1NewVel - object1.velocity[0])/(dt*5)
			#object2.acceleration[0] += float(obj2NewVel - object2.velocity[0])/(dt*5)

			if object1.velocity[0]*sign > 0:
				#print "Place3"
				#print object1.__class__.__name__ + " is slowed by " + object2.__class__.__name__
				object1.acceleration[0] -= sign*object2.idleDeceleration
				if ( object1.lastAcceleration[0]-object1.acceleration[0] )*sign > 0:
					object2.acceleration[0] += (object1.lastAcceleration[0]-object1.acceleration[0])

			if object2.velocity[0]*sign < 0:
				#print "Place4"
				#print object2.__class__.__name__ + " is slowed by " + object1.__class__.__name__
				object2.acceleration[0] += sign*object1.idleDeceleration
				if ( object2.lastAcceleration[0]-object2.acceleration[0] )*sign < 0:
					object1.acceleration[0] += (object2.lastAcceleration[0]-object2.acceleration[0])

		if object1.velocity[0] == object2.velocity[0] ==  object1.acceleration[0] == object2.acceleration[0] == 0:
			if object1.mass > object2.mass:
				objDisplaced = object2
				newSign = sign
			elif object2.mass > object1.mass:
				objDisplaced = object1
				newSign = -sign
			else:
				if randint( 0, 1 ) != 0:
					objDisplaced = object2
					newSign = sign
				else:
					objDisplaced = object1
					newSign = -sign
			objDisplaced.velocity[0] = 0.01*(float(newSign*clippedArea.width)/dt)/dt
	else:
		sign = -1*cmp( object1.position[1], object2.position[1] )
		if ( object1.velocity[1]*sign > 0 and object1.velocity[1]*sign > object2.velocity[1]*sign ) or ( object2.velocity[1]*sign < 0 and object2.velocity[1]*sign < object2.velocity[1]*sign ):
			#obj1NewVel = float( (object1.velocity[1]*(object1.mass-object2.mass)+2*object2.mass*object2.velocity[1]) )/(object1.mass+object2.mass)
			#obj2NewVel = float( (object2.velocity[1]*(object2.mass-object1.mass)+2*object1.mass*object1.velocity[1]) )/(object1.mass+object2.mass)
			obj1NewVel = float( ( (object1.velocity[1]*object1.mass) + (object2.velocity[1]*object2.mass) ) )/(object1.mass+object2.mass)
			obj2NewVel = obj1NewVel
			
			object1.velocity[1] = obj1NewVel
			object2.velocity[1] = obj2NewVel
			#object1.acceleration[1] += float(obj1NewVel - object1.velocity[1])/(dt*5)
			#object2.acceleration[1] += float(obj2NewVel - object2.velocity[1])/(dt*5)
			
			if object1.velocity[1]*sign > 0:
				#print "Place1"
				#print object1.__class__.__name__ + " is slowed by " + object2.__class__.__name__
				object1.acceleration[1] -= sign*object2.idleDeceleration
				if ( object1.lastAcceleration[1]-object1.acceleration[1] )*sign > 0:
					object2.acceleration[1] += (object1.lastAcceleration[1]-object1.acceleration[1])

			if object2.velocity[1]*sign < 0:
				#print "Place2"
				#print object2.__class__.__name__ + " is slowed by " + object1.__class__.__name__
				object2.acceleration[1] += sign*object1.idleDeceleration
				if ( object2.lastAcceleration[1]-object2.acceleration[1] )*sign < 0:
					object1.acceleration[1] += (object2.lastAcceleration[1]-object2.acceleration[1])
		
		if object1.velocity[1] == object2.velocity[1] ==  object1.acceleration[1] == object2.acceleration[1] == 0:
			if object1.mass > object2.mass:
				objDisplaced = object2
				newSign = sign
			elif object2.mass > object1.mass:
				objDisplaced = object1
				newSign = -sign
			else:
				if randint( 0, 1 ) != 0:
					objDisplaced = object2
					newSign = sign
				else:
					objDisplaced = object1
					newSign = -sign
			objDisplaced.velocity[1] = 0.01*(float(newSign*clippedArea.height)/dt)/dt

		
#	I want a function for completely inelastic collisions, for objects that will stop eachother but will not move eachother, or bounce off eachother.
#
#	I need to decide which direction they are hitting eachother from, and negate velocity in that direction.
#	
#	When two objects collide, get the x and y overlap of the objects. the smaller of the overlaps is the most recent, and is logically the "illegal" overlap.
#	So negate all velocity in that direction. And possibly "snap" back that displacement to stop them from even slighty penetrating.

#def inelasticCollideOneRect( foreverAloneObject, clippedArea ):
#	if clippedArea.width < clippedArea.height:
#		dx = foreverAloneObject.rect.centerx - clippedArea.centerx
#		if dx != 0:
#			sign = dx/abs(dx)
#		else:
#			sign = 1
#		
#		foreverAloneObject.position[0] -= sign*clippedArea.width
#		#foreverAloneObject.acceleration[0] += 2100*sign
#		#if sign*foreverAloneObject.velocity[0] < 0:
#		#	foreverAloneObject.velocity[0] = 0
#	else:
#		dy = foreverAloneObject.rect.centery - clippedArea.centery
#		if dy != 0:
#			sign = dy/abs(dy)
#		else:
#			sign = 1
#		foreverAloneObject.position[1] -= sign*clippedArea.height
		#foreverAloneObject.acceleration[1] += 2100*sign
		#if sign*foreverAloneObject.velocity[1] < 0:
		#	foreverAloneObject.velocity[1] = 0

#def inelasticCollideRects( object1, object2, clippedArea ):
	#if clippedArea.width < clippedArea.height:
	#	#SNAPWIDTH
	#	#Snap back the width on the second object. This means the first object displaces/is not displaced by the second.
	#	if clippedArea.centerx < object2.rect.centerx:
	#		#object2.rect.left += clippedArea.width
	#		#Negate any x-velocity towards the clippedArea.
	#		object2.acceleration[0] += 1000
	#		if object2.velocity[0] < 0:
	#			object2.velocity[0] = 0
	#	else:
	#		#object2.rect.left -= clippedArea.width
	#		object2.acceleration[0] -= 1000
	#		if object2.velocity[0] > 0:
	#			object2.velocity[0] = 0
	#else:
	#	#SNAPHEIGHT
	#	#Snap back the height on the second object. This means the first object displaces/is not displaced by the second.
	#	if clippedArea.centery < object2.rect.centery:
	#		#object2.rect.top += clippedArea.height
	#		#Negate any y-velocity towards the clippedArea.
	#		object2.acceleration[1] += 1000
	#		if object2.velocity[1] < 0:
	#			object2.velocity[1] = 0
	#	else:
	#		#object2.rect.top -= clippedArea.height
	#		object2.acceleration[1] -= 1000
	#		if object2.velocity[1] > 0:
	#			object2.velocity[1] = 0
#	if clippedArea.width < clippedArea.height:
#		dx = object1.rect.centerx - object2.rect.centerx
#		if dx != 0:
#			sign = dx/abs(dx)
#		else:
#			sign = 1
		
		#object1.acceleration[0] += 2100*sign
		
		#Snap width
#		object2.position[0] -= sign*clippedArea.width

#		if sign*object1.velocity[0] < 0:
#			object2.acceleration[0] += 10*object1.velocity[0]
		#	object1.velocity[0] = 0
		#object2.acceleration[0] += -2100*sign
#		if sign*object2.velocity[0] > 0:
#			object1.acceleration[0] += 10*object2.velocity[0]
		#	object2.velocity[0] = 0
#	else:
#		dy = object1.rect.centery - object2.rect.centery
#		if dy != 0:
#			sign = dy/abs(dy)
#		else:
#			sign = 1
#
#		#object1.acceleration[1] += 2100*sign

		#Snap height
#		object2.position[1] -= sign*clippedArea.height
		
#		if sign*object1.velocity[1] < 0:
#			object2.acceleration[1] += 10*object1.velocity[1]
			#object1.velocity[1] = 0
		#object2.acceleration[1] += -2100*sign
#		if sign*object2.velocity[1] > 0:
#			object1.acceleration[1] += 10*object2.velocity[1]
#			#object2.velocity[1] = 0

#def inelasticCollidePixelsVsRect( pixObject, rectObject, clippedArea ):
#	intersectGrid = pixObject.collideMask.getGridFromRect( clippedArea )
#	truthArea = intersectGrid.getTrueBox()
#	truthRect = pygame.Rect( truthArea[0], truthArea[1], truthArea[2], truthArea[3] )
#	inelasticCollideRects( pixObject, rectObject, truthRect )

#def inelasticCollidePixels( object1, object2, clippedArea ):
#	intersectGrid = object1.getGridFromRect( clippedArea ).mergeWith( object2.getGridFromRect( clippedArea ), 'and' )
#	truthArea = intersectGrid.getTrueBox()
#	truthRect = pygame.Rect( truthArea[0], truthArea[1], truthArea[2], truthArea[3] )
#	inelasticCollideRects( object1, object2, truthRect )
