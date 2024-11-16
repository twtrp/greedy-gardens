from src.library.essentials import *
from src.template.BaseState import BaseState
from src.classes.Button import Button

class Play_EndDayState(BaseState):
    def __init__(self, game, parent, stack):
        BaseState.__init__(self, game, parent, stack)
        self.parent = parent
        
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
            
        self.button_list = []

        self.load_assets()
            
    def load_assets(self):
        self.title_font = fonts.lf2
        self.text_font = fonts.lf2

        self.button_list.append(Button(
            game=self.game,
            id='bg',
            width=constants.canvas_width - 2 * self.parent.box_width,
            height=constants.canvas_height,
            pos=((self.parent.box_width, 0)),
            pos_anchor='topleft'
        ))

    def update(self, dt, events):
        
        for button in self.button_list:
            button.update(dt=dt, events=events)
            if button.hovered:
                if button.hover_cursor is not None:
                    self.cursor = button.hover_cursor
            if button.clicked:
                if button.id == 'bg':
                    print("exiting end day")
                    self.parent.endDayState = True
                    self.exit_state()

    def render(self, canvas):
        for button in self.button_list:
                button.render(canvas)
        
        utils.draw_rect(dest=canvas,
                        size=(constants.canvas_width - 2*self.parent.box_width, constants.canvas_height),
                        pos=(self.parent.box_width, 0),
                        pos_anchor='topleft',
                        color=(*colors.black, 128),
                        inner_border_width=0,
                        outer_border_width=0,
                        outer_border_color=colors.black)

        # Title text
        title_text = utils.get_text(
            text=f"Day {self.current_day} Result", 
            font=fonts.lf2, 
            size='huge', 
            color=colors.white
        )
        title_x = (constants.canvas_width - title_text.get_width()) // 2
        canvas.blit(title_text, (title_x, 150))
        
        # Center vertically
        center_y = constants.canvas_height // 2
        
        if self.current_fruit:
            # Fruit sprite on left side
            big_fruit_name = self.current_fruit.replace('fruit_', 'fruit_big_')
            fruit_sprite = utils.get_sprite(spritesheets.fruit_32x32, big_fruit_name)
            scaled_fruit_sprite = pygame.transform.scale_by(surface=fruit_sprite, factor=2)
            fruit_x = (constants.canvas_width // 2) - scaled_fruit_sprite.get_width() - 20
            canvas.blit(scaled_fruit_sprite, (fruit_x, center_y - scaled_fruit_sprite.get_height() // 2))
            
            score_text = utils.get_text(
                text=f"Score: {self.current_score}", 
                font=fonts.lf2, 
                size='medium', 
                color=colors.white
            )
            score_x = (constants.canvas_width // 2) + 20
            canvas.blit(score_text, (score_x, center_y - score_text.get_height() // 2))
        
        # Click to continue text
        continue_text = utils.get_text(
            text="Click anywhere to continue", 
            font=fonts.lf1, 
            size='small', 
            color=colors.white
        )
        continue_x = (constants.canvas_width - continue_text.get_width()) // 2
        canvas.blit(continue_text, (continue_x, constants.canvas_height - 100))
        