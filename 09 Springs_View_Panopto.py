import random
import math
import pygame
import PyParticles

def createSpring(particleOne, particleTwo, springLength):
    #get the IDs of two particles given we have the objects
    index1 = universe.particles.index(particleOne)
    index2 = universe.particles.index(particleTwo)
    universe.addSpring(index1, index2, springLength)


clock = pygame.time.Clock()

#set up the environment and the screen
(width, height) = (800, 800)
screen = pygame.display.set_mode((width, height))

pygame.display.set_caption('Springs')

#set up the environment
universe = PyParticles.Environment((width, height))
universe.colour = (255,255,255)
universe.addFunctions(['move', 'bounce', 'collide', 'drag', 'accelerate'])
universe.acceleration = (math.pi, 0.01)


#add some particles to the screen
for p in range(10):
    universe.addParticles(mass=100, size=16, speed=2, elasticity=1, colour=(20,40,200))




paused = False
running = True

selected_particle = None
spring_select_one = None
spring_select_two = None
selecting_springs = False
corner_text = ""
spring_size = 150
font = pygame.font.init()
font = pygame.font.SysFont('Courier', 16)

#game loop
while running:

    #update if we are not paused
    if not paused:
        universe.update()
        
    screen.fill(universe.colour)
    
    #draw the particles and springs
    for p in universe.particles:
        pygame.draw.circle(screen, p.colour, (int(p.x), int(p.y)), p.size, 0)
    
    for s in universe.springs:
        pygame.draw.aaline(screen, (0,0,0), (int(s.p1.x), int(s.p1.y)), (int(s.p2.x), int(s.p2.y)))
    
    #event handlers
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        #change the paused state when space is pressed
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = (True, False)[paused]
            elif event.key == pygame.K_LCTRL:
                selecting_springs = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LCTRL:
                if spring_select_one and spring_select_two:
                    #lets draw the springs!
                    createSpring(spring_select_one, spring_select_two, spring_size)
                selecting_springs = False
                spring_select_one = None
                spring_select_two = None
                corner_text = ""


        #deal with a mouse selection
        elif event.type == pygame.MOUSEBUTTONDOWN:
            #check if they have clicked on a particle
            (mouseX, mouseY) = event.pos
            selected_particle = universe.findParticle(mouseX, mouseY)
            if selected_particle and selecting_springs:
                if spring_select_one:
                    spring_select_two = selected_particle
                    corner_text = "Spring size: "+ str(spring_size)
                    #wait until they have released the CTRL button, enable length select
                    #createSpring(spring_select_one, spring_select_two)
                else:
                    spring_select_one = selected_particle
                selected_particle = None
            
        elif event.type == pygame.MOUSEBUTTONUP:
            selected_particle = None
        elif selected_particle and event.type == pygame.MOUSEMOTION:
            (mouseX, mouseY) = event.pos
            selected_particle.mouseMove(mouseX, mouseY)
            selected_particle.x = mouseX
            selected_particle.y = mouseY
        elif event.type == pygame.MOUSEWHEEL:
            if spring_select_two:
                spring_size += event.y
                corner_text = "Spring size: "+ str(spring_size)
    
    text = font.render(corner_text, True, (0,0,0), universe.colour) 
    # create a rectangular object for the
    # text surface object
    textRect = text.get_rect()
    # set the center of the rectangular object.
    textRect.bottomright = (width, height)
    screen.blit(text, textRect)

    #make sure we limit the framerate, and draw. 
    clock.tick(60)
    pygame.display.flip()

