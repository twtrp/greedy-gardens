from src.library.essentials import *

class Button:
   def __init__(self,
                game: object,
                id: str,
                group: str = 'default',
                surface: pygame.Surface = None,
                width: int = 0,
                height: int = 0,
                pos: tuple = (0, 0),
                pos_anchor: str = posanchors.topleft,
                padding_x: int = 0,
                padding_y: int = 0,
                enable_click: bool = True,
                hover_cursor: dict = cursors.hand):
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
       canvas_aspect_ratio = constants.canvas_width / constants.canvas_height
       screen_aspect_ratio = self.game.screen_width / self.game.screen_height

       if screen_aspect_ratio > canvas_aspect_ratio:
           scale_factor = self.game.screen_height / constants.canvas_height
           offset_x = (self.game.screen_width - int(constants.canvas_width * scale_factor)) // 2
           scale_x = scale_factor
           scale_y = scale_factor
       else:
           scale_factor = self.game.screen_width / constants.canvas_width
           offset_y = (self.game.screen_height - int(constants.canvas_height * scale_factor)) // 2
           scale_x = scale_factor
           scale_y = scale_factor

       self.padding_x = self.para_padding_x * scale_x
       self.padding_y = self.para_padding_y * scale_y

       actual_width = (self.para_width * scale_x if self.para_width != 0 else surface.get_width() * scale_x) + 2 * self.padding_x
       actual_height = (self.para_height * scale_y if self.para_height != 0 else surface.get_height() * scale_y) + 2 * self.padding_y

       self.surface = pygame.Surface((actual_width, actual_height), pygame.SRCALPHA)
       button_surface = surface if surface is not None else pygame.Surface((self.para_width, self.para_height))
       scaled_button_surface = pygame.transform.scale(button_surface, (int(actual_width - 2 * self.padding_x), int(actual_height - 2 * self.padding_y)))
       self.surface.blit(scaled_button_surface, (self.padding_x, self.padding_y))

       self.rect = self.surface.get_rect()

   def update_scale(self):
       canvas_aspect_ratio = constants.canvas_width / constants.canvas_height
       screen_aspect_ratio = self.game.screen_width / self.game.screen_height

       if screen_aspect_ratio > canvas_aspect_ratio:
           scale_factor = self.game.screen_height / constants.canvas_height
           scale_x = scale_factor
           scale_y = scale_factor
       else:
           scale_factor = self.game.screen_width / constants.canvas_width
           scale_x = scale_factor
           scale_y = scale_factor

       self.scale_x = scale_x
       self.scale_y = scale_y
       self.padding_x = self.para_padding_x * self.scale_x
       self.padding_y = self.para_padding_y * self.scale_y

   def toggle_click(self, enable: bool):
       self.enable_click = enable

   def set_pos(self, pos: tuple, pos_anchor: str):
       canvas_aspect_ratio = constants.canvas_width / constants.canvas_height
       screen_aspect_ratio = self.game.screen_width / self.game.screen_height

       if screen_aspect_ratio > canvas_aspect_ratio:
           scale_factor = self.game.screen_height / constants.canvas_height
           offset_x = (self.game.screen_width - int(constants.canvas_width * scale_factor)) // 2
           scaled_x = pos[0] * scale_factor + offset_x
           scaled_y = pos[1] * scale_factor
       else:
           scale_factor = self.game.screen_width / constants.canvas_width
           offset_y = (self.game.screen_height - int(constants.canvas_height * scale_factor)) // 2
           scaled_x = pos[0] * scale_factor
           scaled_y = pos[1] * scale_factor + offset_y

       setattr(self.rect, pos_anchor, (scaled_x, scaled_y))

   def check_collision(self, pos):
       return self.rect.collidepoint(pos)

   def update(self, dt, events):
       new_canvas_aspect_ratio = constants.canvas_width / constants.canvas_height
       new_screen_aspect_ratio = self.game.screen_width / self.game.screen_height

       if new_screen_aspect_ratio != self.scale_x or new_screen_aspect_ratio != self.scale_y:
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
       pass