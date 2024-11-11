import pygame
import sys

# Initialize pygame
pygame.init()

# Screen dimensions and setup
screen_width, screen_height = 800, 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Circular Mask Example")

# Circle Mask Properties
circle_radius = 300
circle_center = (screen_width // 2, screen_height // 2)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Render your existing content here
    screen.fill((255,0,0))  # Example background, replace with your actual content
    # You can add any other rendering here, like images or shapes.
    
    # Create the mask surface with black color and transparency
    mask_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    mask_surface.fill((0, 0, 0))  # Fill with black

    # Punch a circular hole in the mask
    pygame.draw.circle(mask_surface, (0, 0, 0, 0), circle_center, circle_radius)

    # Blit the mask on top of everything
    screen.blit(mask_surface, (0, 0))

    # Update the display
    pygame.display.flip()

# Quit pygame
pygame.quit()
sys.exit()
