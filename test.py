import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pygame Textbox Demo")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (135, 206, 250)

# Fonts
FONT = pygame.font.Font(None, 32)

# Textbox settings
textbox_rect = pygame.Rect(100, 200, 440, 50)
color_active = pygame.Color('dodgerblue2')
color_inactive = pygame.Color('lightskyblue3')
color = color_inactive
active = False
text = ''

def main():
    global active, color, text

    clock = pygame.time.Clock()
    running = True

    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                print(active)
                # Check if the mouse is within the textbox area
                if textbox_rect.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive

            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        print("Text entered:", text)
                        text = ''
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        # Draw background
        screen.fill(WHITE)

        # Render the text
        txt_surface = FONT.render(text, True, BLACK)

        # Resize textbox if text is too wide
        textbox_rect.w = max(440, txt_surface.get_width() + 10)
        
        # Draw elements
        pygame.draw.rect(screen, color, textbox_rect, 2)
        screen.blit(txt_surface, (textbox_rect.x + 5, textbox_rect.y + 5))

        # Update the display
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
