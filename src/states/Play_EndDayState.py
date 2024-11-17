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
        # Text
        self.result_title = utils.get_text(text=f'Day {self.current_day} Result', font=fonts.lf2, size='large', color=colors.white)
        self.vs_title = utils.get_text(text=f'vs', font=fonts.lf2, size='medium', color=colors.mono_175)
        self.pass_title = utils.get_text(text=f'Pass!', font=fonts.lf2, size='medium', color=colors.green_light)
        self.fail_title = utils.get_text(text=f'Fail!', font=fonts.lf2, size='medium', color=colors.red_light)

        self.result_list = []
        if self.parent.current_day == 1:
            self.result_list.append({
                                    'text': str(getattr(self.parent, f'final_day{self.parent.current_day}_score')),
                                    'fruit': getattr(self.parent, f'day{self.parent.current_day}_fruit'),
                                    })
        elif self.parent.current_day < self.parent.day:
            self.result_list.append({
                                    'text': str(getattr(self.parent, f'final_day{self.parent.current_day - 1}_score')),
                                    'fruit': getattr(self.parent, f'day{self.parent.current_day - 1}_fruit'),
                                    })
            self.result_list.append({
                                    'text': str(getattr(self.parent, f'final_day{self.parent.current_day}_score')),
                                    'fruit': getattr(self.parent, f'day{self.parent.current_day}_fruit'),
                                    })
        self.result_sureface_list = []
        for i, option in enumerate(self.result_list):
                text = utils.get_text(text=option['text'], font=fonts.lf2, size='medium', color=colors.white)
                fruit = utils.get_sprite(spritesheets.fruit_16x16, self.current_fruit)
                scaled_fruit_image = pygame.transform.scale_by(surface=fruit, factor=3)
                glow_fruit_image = utils.effect_outline(surface=scaled_fruit_image, distance=2, color=colors.white)
                self.result_sureface_list.append({
                    'surface': text,
                    'surface_fruit': glow_fruit_image,
                })
        self.parent.endDayState = False
        
        self.button_list.append(Button(
            game=self.game,
            id='bg',
            width=constants.canvas_width - 2 * self.parent.box_width,
            height=constants.canvas_height,
            pos=((self.parent.box_width, 0)),
            pos_anchor='topleft'
        ))
        self.continue_text = utils.get_text(text="Click anywhere to continue", font=fonts.lf2, size='small', color=colors.white)
        
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
                        color=(*colors.black, 128), # 50% transparency
                        inner_border_width=0,
                        outer_border_width=0,
                        outer_border_color=colors.black)

        # Title text
        utils.blit(dest=canvas, source=self.result_title, pos=(constants.canvas_width/2, constants.canvas_height/2 - 150), pos_anchor='center')
        if self.parent.current_day > 1:
            utils.blit(dest=canvas, source=self.vs_title, pos=(constants.canvas_width/2, constants.canvas_height/2  - 5), pos_anchor='center')
            if getattr(self.parent, f'final_day{self.parent.current_day}_score') <= getattr(self.parent, f'final_day{self.parent.current_day -1}_score'):
                utils.blit(dest=canvas, source=self.fail_title, pos=(constants.canvas_width/2, 500), pos_anchor='center')
            else:
                utils.blit(dest=canvas, source=self.pass_title, pos=(constants.canvas_width/2, 500), pos_anchor='center')
                
        
        # Fruit and score
        for i, option in enumerate(self.result_sureface_list):
            utils.blit(dest=canvas, source=option['surface_fruit'], pos=(constants.canvas_width/2 - 25, 305 + i*110), pos_anchor='center')
            utils.blit(dest=canvas, source=option['surface'], pos=(constants.canvas_width/2 + 25, 305 + i*110), pos_anchor='center')
        
        # Continue text
        utils.blit(dest=canvas, source=self.continue_text, pos=(constants.canvas_width/2, constants.canvas_height-self.continue_text.get_height()+5), pos_anchor='center')
        