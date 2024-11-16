from src.library.essentials import *
from src.template.BaseState import BaseState
from src.library import utils
from src.library.resources import spritesheets
from src.library.essentials import constants
import pygame

class Play_EndDayState(BaseState):
    def __init__(self, game, parent, stack):
        BaseState.__init__(self, game, parent, stack)
        self.parent = parent

        self.load_assets()
        
        # Get current day's info
        self.current_day = self.parent.current_day
        if self.current_day == 1:
            self.current_score = self.parent.day1_score
            self.current_fruit = self.parent.day1_fruit
        elif self.current_day == 2:
            self.current_score = self.parent.day2_score
            self.current_fruit = self.parent.day2_fruit
        elif self.current_day == 3:
            self.current_score = self.parent.day3_score
            self.current_fruit = self.parent.day3_fruit
        else:
            self.current_score = self.parent.day4_score
            self.current_fruit = self.parent.day4_fruit
            
    def load_assets(self):
        self.title_font = pygame.font.Font(None, 48)
        self.text_font = pygame.font.Font(None, 36)

    def update(self, dt, events):
        mouse_pos = pygame.mouse.get_pos()
        
        # Check if mouse is in game board area (not in GUI areas)
        if (mouse_pos[0] > self.parent.box_width and 
            mouse_pos[0] < constants.canvas_width - self.parent.box_width):
            
            if pygame.mouse.get_pressed()[0]:  # Left click
                self.parent.drawing = False
                self.parent.placing = False
                self.parent.eventing = False
                self.exit_state()

    def render(self, canvas):
        # Draw translucent black rectangle
        utils.draw_rect(dest=canvas,
            size=(constants.canvas_width - 2*self.parent.box_width, constants.canvas_height),
            pos=(self.parent.box_width, 0),
            pos_anchor='topleft',
            color=(*colors.black, 128),
            inner_border_width=0,
            outer_border_width=0,
            outer_border_color=colors.black)
        
        # Title
        title_text = self.title_font.render(f"Day {self.current_day} Result", True, (255, 255, 255))
        title_x = (constants.canvas_width - title_text.get_width()) // 2
        canvas.blit(title_text, (title_x, 150))
        
        # Center vertically
        center_y = constants.canvas_height // 2
        
        if self.current_fruit:
            # Fruit sprite on left side
            fruit_sprite = utils.get_sprite(spritesheets.fruit_16x16, self.current_fruit)
            scaled_fruit_sprite = pygame.transform.scale_by(surface=fruit_sprite, factor=2)
            fruit_x = (constants.canvas_width // 2) - scaled_fruit_sprite.get_width() - 20
            canvas.blit(scaled_fruit_sprite, (fruit_x, center_y - scaled_fruit_sprite.get_height() // 2))
            
            # Score text on right side
            score_text = self.text_font.render(f"Score: {self.current_score}", True, (255, 255, 255))
            score_x = (constants.canvas_width // 2) + 20
            canvas.blit(score_text, (score_x, center_y - score_text.get_height() // 2))
        
        # Click text only at bottom
        continue_text = self.text_font.render("Click anywhere to continue", True, (255, 255, 255))
        continue_x = (constants.canvas_width - continue_text.get_width()) // 2
        canvas.blit(continue_text, (continue_x, constants.canvas_height - 100))
