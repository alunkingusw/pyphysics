import random
import pygame
import PyParticles
clock = pygame.time.Clock()
(width, height) = (800, 800)
screen = pygame.display.set_mode((width, height))

universe = PyParticles.Environment((width, height))
universe.colour=(0,0,0)
universe.addFunctions(['move', 'attract', 'combine'])

def calculateRadius(mass):
    return mass**(0.5)

#create 100 white particles
for p in range(100):
    particle_mass = random.randint(1,4)
    particle_size = calculateRadius(particle_mass)
    universe.addParticles(mass=particle_mass, size=particle_size, colour=(255,255,255))

running = True
while running:
    universe.update()
    screen.fill(universe.colour)

    particles_to_remove = []

    for p in universe.particles:
        if 'collide_with' in p.__dict__:
            particles_to_remove.append(p.collide_with)
            p.size = calculateRadius(p.mass)
            del p.__dict__['collide_with']

        if p.size < 2:
            pygame.draw.rect(screen, p.colour, (int(p.x), int(p.y), 2, 2))
        else:
            pygame.draw.circle(screen, p.colour, (int(p.x), int(p.y)), int(p.size), 0)
    
    for p in particles_to_remove:
        if p in universe.particles:
            universe.particles.remove(p)

    clock.tick(60)
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False