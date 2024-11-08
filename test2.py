import pygame

class TextBox:
    def __init__(self, x, y, w, h, font, text='', color=(255, 255, 255), bg_color=(0, 0, 0), border_color=(255, 255, 255), border_width=2):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.bg_color = bg_color
        self.border_color = border_color
        self.border_width = border_width
        self.font = font
        self.text = text
        self.text_surface = font.render(text, True, color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Toggle active state if clicked inside the textbox
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.active = False  # Optionally deactivate on Enter key
            else:
                self.text += event.unicode
            # Re-render the text
            self.text_surface = self.font.render(self.text, True, self.color)

    def update(self):
        # Adjust the width of the text box if necessary
        width = max(200, self.text_surface.get_width() + 10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        screen.fill(self.bg_color, self.rect)
        screen.blit(self.text_surface, (self.rect.x + 5, self.rect.y + 5))
        # Draw the rect border
        pygame.draw.rect(screen, self.border_color, self.rect, self.border_width)


# Example usage:
pygame.init()
screen = pygame.display.set_mode((500, 300))
pygame.display.set_caption("TextBox Example")

font = pygame.font.Font(None, 32)
textbox = TextBox(100, 100, 200, 32, font)
textbox2 = TextBox(100, 200, 300, 32, font, 'Hi')

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        textbox.handle_event(event)
        textbox2.handle_event(event)

    textbox.update()
    textbox2.update()

    screen.fill((30, 30, 30))
    textbox.draw(screen)
    textbox2.draw(screen)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
