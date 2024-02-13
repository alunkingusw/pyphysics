import math
from pickle import TRUE
import random
import pygame

def collide(p1, p2):
    #get the relative coordinates
    dx = p1.x - p2.x
    dy = p1.y - p2.y
    
    #work out the hypotenuse of the triangle formed
    distance = math.hypot(dx, dy)
    #compare it with the sizes of the circles
    if distance < p1.size + p2.size:

        #work out angle of collision
        angle = math.atan2(dy, dx) + 0.5 * math.pi

        #get total mass of particles
        total_mass = p1.mass + p2.mass

        temp_speed = p1.speed

        #combine vectors
        (p1.angle, p1.speed) = addVectors(p1.angle, p1.speed*(p1.mass-p2.mass)/total_mass, angle, 2*p2.speed*p2.mass/total_mass)
        (p2.angle, p2.speed) = addVectors(p2.angle, p2.speed*(p2.mass-p1.mass)/total_mass, angle+math.pi, 2*p1.speed*p1.mass/total_mass)

        #reduce speed due to collision
        p1.speed *= p1.elasticity
        p2.speed *= p2.elasticity

        #move the particles away from each other to prevent constant collision
        overlap = 0.5 * (p1.size + p2.size - distance + 1)
        p1.x += math.sin(angle) * overlap
        p1.y -= math.cos(angle) * overlap
        p2.x -= math.sin(angle) * overlap
        p2.y += math.cos(angle) * overlap


#combines two vectors to create a new one
def addVectors(angle1, length1, angle2, length2):
    x = math.sin(angle1) * length1 + math.sin(angle2) * length2
    y = math.cos(angle1) * length1 + math.cos(angle2) * length2
    length = math.hypot(x,y)
    angle = 0.5 * math.pi - math.atan2(y, x)
    return (angle, length)

class Particle:
    drag = 0.999
    elasticity = 0.75

    def __init__(self, x, y, size, mass=1):
        self.x = x
        self.y = y
        self.size = size
        self.mass = mass
        self.colour = (0, 0, 255)
        self.thickness = 1
        self.speed = 0.01
        self.angle = math.pi

    def move(self):
        self.x += math.sin(self.angle) * self.speed
        self.y -= math.cos(self.angle) * self.speed

    def addDrag(self):
        self.speed *= self.drag

    #apply a force to the object, could be used for gravity or another propulsive force
    def accelerate(self, vector):
        (self.angle, self.speed) = addVectors(self.angle, self.speed, vector[0], vector[1])
    
    def mouseMove(self, x, y):
        #get difference from previous position
        dx = x - self.x
        dy = y - self.y
        #work out relative angle and speed
        self.angle = 0.5*math.pi + math.atan2(dy, dx)
        self.speed = math.hypot(dx, dy) * 0.01

    def attract(self, otherParticle):
        #work out the distance between the particles
        dx = (self.x - otherParticle.x)
        dy = (self.y - otherParticle.y)
        dist = math.hypot(dx, dy)

        #get the angle between then
        theta = math.atan2(dy, dx)

        #work out the force
        force = 0.2 * self.mass * otherParticle.mass / dist ** 2

        #apply the force
        self.accelerate((theta - 0.5 * math.pi, force/self.mass))
        otherParticle.accelerate((theta + 0.5 * math.pi, force/otherParticle.mass))

    def combine(self, otherParticle):
        #check if the particles are touching
        dx = (self.x - otherParticle.x)
        dy = (self.y - otherParticle.y)
        dist = math.hypot(dx, dy)

        if dist < self.size + otherParticle.size:
            #work out the mass of the particles, then create a new particle
            total_mass = self.mass + otherParticle.mass
            self.x = (self.x * self.mass + otherParticle.x*otherParticle.mass)/total_mass
            self.y = (self.y * self.mass + otherParticle.y*otherParticle.mass)/total_mass

            #combine the vector of the two particles
            (self.angle, self.speed) = addVectors(self.angle, self.speed*self.mass/total_mass, otherParticle.angle, otherParticle.speed*otherParticle.mass/total_mass)
            
            #account for collision energy
            self.speed *= (self.elasticity * otherParticle.elasticity)

            #set the new mass
            self.mass = total_mass

            #indicate a collision has occured
            self.collide_with = otherParticle

class Spring:
    def __init__(self, p1, p2, length=50, strength=0.5):
        self.p1 = p1
        self.p2 = p2
        self.length = length
        self.strength = strength
    
    #exert the forces between the springs
    def update(self):
        #word out the distance between the two particles
        dx = self.p1.x - self.p2.x
        dy = self.p1.y - self.p2.y
        dist = math.hypot(dx, dy)

        theta = math.atan2(dy, dx)

        #note we don't attract once the length has been reached - we repel
        force = (self.length - dist) * self.strength

        self.p1.accelerate((theta + 0.5 * math.pi, force/self.p1.mass))
        self.p2.accelerate((theta - 0.5 * math.pi, force/self.p2.mass))

class Environment:
    

    def __init__(self, size):
        (width, height) = size
        self.width = width
        self.height = height
        self.particles = []
        self.springs = []
        self.colour = (255,255,255)
        self.mass_of_air = 0.5
        self.hasBoundaries = TRUE
        self.gravity = (math.pi, 0.005)

        #set up empty functions for enabled features
        self.particle_functions1=[]
        self.particle_functions2=[]

        #add possible interaction functions
        self.function_dictionary = {
            'move': (1, lambda p: p.move()),
            'drag': (1, lambda p: p.addDrag()),
            'bounce': (1, lambda p: self.bounce(p)), #bounce is called in environment
            'accelerate': (1, lambda p: p.accelerate(self.gravity)),
            'collide': (2, lambda p1, p2: collide(p1,p2)),
            'attract' : (2, lambda p1, p2: p1.attract(p2)),
            'combine' : (2, lambda p1, p2: p1.combine(p2))
        }


    def addFunctions(self, function_list):
        for f in function_list:
            #try and get function, provide default values in event of failure
            (n, func) = self.function_dictionary.get(f, (-1, None))
            #single particle function
            if n == 1:
                self.particle_functions1.append(func)
            
            #two particle function
            elif n == 2:
                self.particle_functions2.append(func)
            else:
                print("No function found called %s" %f)

    #used to locate where the mouse clicked
    def findParticle(self, x, y):
        for p in self.particles:
            if math.hypot(p.x-x, p.y-y) <= p.size:
                return p

    def bounce(self, particle):
        #check east wall
        if particle.x > self.width - particle.size:
            particle.speed *= particle.elasticity
            particle.x = 2 * (self.width - particle.size) - particle.x
            particle.angle = - particle.angle
        #check west wall
        elif particle.x < particle.size:
            particle.speed *= particle.elasticity
            particle.x = 2 * particle.size - particle.x
            particle.angle = - particle.angle
        #check south wall
        if particle.y > self.height - particle.size:
            particle.speed *= particle.elasticity
            particle.y = 2 * (self.height - particle.size) - particle.y
            particle.angle = math.pi - particle.angle
        #check north wall
        elif particle.y < particle.size:
            particle.speed *= particle.elasticity
            particle.y = 2 * particle.size - particle.y
            particle.angle = math.pi - particle.angle

    def addParticles(self, n=1, **kargs):

        for i in range(n):
            #try and get an argument, if it fails, generate a random number instead
            size = kargs.get('size', random.randint(10, 20))
            mass = kargs.get('mass', random.randint(100, 10000))
            x = kargs.get('x', random.uniform(size, self.width-size))
            y = kargs.get('y', random.uniform(size, self.height-size))

            #create the particle
            p = Particle(x, y, size, mass)

            #add additional attributes
            p.speed = kargs.get('speed', random.random())
            p.angle = kargs.get('angle', random.uniform(0, math.pi*2))
            p.colour = kargs.get('colour', (0, 0, 255))
            p.drag = (p.mass/(p.mass + self.mass_of_air)) ** p.size

            #add to the collection of particles
            self.particles.append(p)

    def addSpring(self, p1, p2, length=50, strength=0.5):
        #add a spring to the environment between the two given particles
        self.springs.append(Spring(self.particles[p1], self.particles[p2], length, strength))


    def update(self):

        #exert spring forces
        for spring in self.springs:
            spring.update()

        #loop through all particles
        for i, particle in enumerate(self.particles):
            #call single particle functions
            for f in self.particle_functions1:
                f(particle)
            
            if(self.particle_functions2 != []):
                for particle2 in self.particles[i+1:]:
                    #call two particle functions
                    for f in self.particle_functions2:
                        f(particle, particle2)
            
