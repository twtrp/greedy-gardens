import pygame

pygame.init()
screen = pygame.display.set_mode((500, 500), flags = pygame.HWSURFACE|pygame.DOUBLEBUF)
clock = pygame.time.Clock()
running = True

full_screen = False

icon = pygame.Surface((32, 32))
icon.fill("red")
pygame.display.set_icon(icon)

while running:
  for event in pygame.event.get():
      if event.type == pygame.QUIT:
          running = False
      if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
          if not full_screen:
              screen = pygame.display.set_mode((0, 0), flags = pygame.FULLSCREEN | pygame.HWSURFACE|pygame.DOUBLEBUF)
          else:
              screen = pygame.display.set_mode((500, 500), flags = pygame.HWSURFACE|pygame.DOUBLEBUF)

          full_screen = not full_screen

  screen.fill("lightgreen")
  screen.blit(icon, (10,10))

  pygame.display.flip()

  clock.tick(60) 

pygame.quit()