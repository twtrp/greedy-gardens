from src.library.essentials import *
import pygame

class Button:
    def __init__(
            self,
            game: object,
            id: str,
            group: str = 'default',
            surface: pygame.Surface = None,
            width: int = 0,
            height: int = 0,
            pos: tuple = (0, 0),
            pos_anchor: str = 'topleft',
            padding_x: int = 0,
            padding_y: int = 0,
            enable_click: bool = True,
            hover_cursor: dict = cursors.hand
        ):
        self.game = game
        self.id = id
        self.group = group
        self.para_width = width
        self.para_height = height
        self.para_padding_x = padding_x
        self.para_padding_y = padding_y
        self.pos = pos
        self.pos_anchor = pos_anchor
        self.hovered = False
        self.pressed = False
        self.clicked = False
        self.enable_click = enable_click
        self.hover_cursor = hover_cursor

        self.update_scale()
        self.create_surface(surface)
        self.set_pos(self.pos, self.pos_anchor)

    def create_surface(self, surface):
        self.scale_x = self.game.screen_width / constants.canvas_width
        self.scale_y = self.game.screen_height / constants.canvas_height
        self.padding_x = self.para_padding_x * self.scale_x
        self.padding_y = self.para_padding_y * self.scale_y

        actual_width = (self.para_width * self.scale_x if self.para_width != 0 else surface.get_width() * self.scale_x) + 2 * self.padding_x
        actual_height = (self.para_height * self.scale_y if self.para_height != 0 else surface.get_height() * self.scale_y) + 2 * self.padding_y

        self.surface = pygame.Surface((actual_width, actual_height), pygame.SRCALPHA)
        button_surface = surface if surface is not None else pygame.Surface((self.para_width, self.para_height))
        scaled_button_surface = pygame.transform.scale(button_surface, (int(actual_width - 2 * self.padding_x), int(actual_height - 2 * self.padding_y)))
        self.surface.blit(scaled_button_surface, (self.padding_x, self.padding_y))

        self.rect = self.surface.get_rect()

    def update_scale(self):
        self.scale_x = self.game.screen_width / constants.canvas_width
        self.scale_y = self.game.screen_height / constants.canvas_height
        self.padding_x = self.para_padding_x * self.scale_x
        self.padding_y = self.para_padding_y * self.scale_y

    def toggle_click(self, enable: bool):
        self.enable_click = enable

    def set_pos(self, pos: tuple, pos_anchor: str):
        setattr(self.rect, pos_anchor, (pos[0] * self.scale_x, pos[1] * self.scale_y))

    def check_collision(self, pos):
        return self.rect.collidepoint(pos)

    def update(self, dt, events):
        new_scale_x = self.game.screen_width / constants.canvas_width
        new_scale_y = self.game.screen_height / constants.canvas_height

        if new_scale_x != self.scale_x or new_scale_y != self.scale_y:
            self.update_scale()
            self.create_surface(self.surface)
            self.set_pos(self.pos, self.pos_anchor)

        pos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(pos)

        if self.enable_click:
            self.clicked = False
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.hovered:
                        self.pressed = True
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if self.hovered and self.pressed:
                        self.clicked = True
                    self.pressed = False
        else:
            self.pressed = False
            self.clicked = False

    def render(self, canvas):
        pygame.draw.rect(canvas, (255, 0, 0), self.rect, 2)
        canvas.blit(self.surface, self.rect.topleft)
