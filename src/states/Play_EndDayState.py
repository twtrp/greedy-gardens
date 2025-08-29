from src.library.essentials import *
from src.template.BaseState import BaseState
from src.classes.Button import Button

class Play_EndDayState(BaseState):
    def __init__(self, game, parent, stack):
        BaseState.__init__(self, game, parent, stack)
        
        # Stop the rightclick hint animation loop
        self.parent.tween_list.clear()
        
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
        elif self.current_day == 4:
            self.current_score = self.parent.day4_score
            self.current_fruit = self.parent.day4_fruit

        # Update score if fail to make more than yesterday
        if self.parent.current_day > 1:
            current_score = getattr(self.parent, f'final_day{self.parent.current_day}_score')
            previous_score = getattr(self.parent, f'final_day{self.parent.current_day - 1}_score')

            # If today's score is not higher than yesterday's
            if current_score <= previous_score:
                # Replace today's score with 0 (or keep it if already negative)
                new_score = current_score if current_score < 0 else 0
                setattr(self.parent, f'final_day{self.parent.current_day}_score', new_score)
                setattr(self.parent, f'day{self.parent.current_day}_score', new_score)
                # Set penalty flag to prevent score recalculation
                setattr(self.parent, f'day{self.parent.current_day}_penalty_applied', True)
            
        self.button_list = []

        self.parent.is_choosing = True

        self.load_assets()
            
    def load_assets(self):
        # Text
        self.result_title = utils.get_text(text=f'Day {self.current_day} Result', font=fonts.lf2, size='large', color=colors.white)
        self.vs_title = utils.get_text(text=f'vs', font=fonts.lf2, size='medium', color=colors.mono_205)
        self.pass_title = utils.get_text(text=f'Pass!', font=fonts.lf2, size='large', color=colors.green_light)
        self.fail_title = utils.get_text(text=f'Fail!', font=fonts.lf2, size='large', color=colors.red_light)
        self.fail_description = utils.get_text(text=f'You failed to collect more than yesterday!', font=fonts.lf2, size='tiny', color=colors.red_light)

        self.result_list = []
        if self.parent.current_day == 1:
            self.result_list.append({
                                    'text': str(getattr(self.parent, f'final_day{self.parent.current_day}_score')),
                                    'fruit': getattr(self.parent, f'day{self.parent.current_day}_fruit'),
                                    })
        elif self.parent.current_day <= self.parent.day:
            self.result_list.append({
                                    'text': str(getattr(self.parent, f'final_day{self.parent.current_day - 1}_score')),
                                    'fruit': getattr(self.parent, f'day{self.parent.current_day - 1}_fruit'),
                                    })
            self.result_list.append({
                                    'text': str(getattr(self.parent, f'final_day{self.parent.current_day}_score')),
                                    'fruit': getattr(self.parent, f'day{self.parent.current_day}_fruit'),
                                    })
        self.result_surface_list = []
        for i, option in enumerate(self.result_list):
                text = utils.get_text(text=option['text'], font=fonts.lf2, size='large', color=colors.white)
                fruit = self.parent.fruit_sprites[option['fruit']]
                scaled_fruit_image = pygame.transform.scale_by(surface=fruit, factor=3)
                glow_fruit_image = utils.effect_outline(surface=scaled_fruit_image, distance=2, color=colors.mono_35)
                if i == 0 and self.parent.current_day != 1:
                    glow_fruit_image = utils.effect_grayscale(surface=glow_fruit_image)
                self.result_surface_list.append({
                    'surface': text,
                    'surface_fruit': glow_fruit_image,
                })
        self.parent.endDayState = False
        
        self.button_list.append(Button(
            game=self.game,
            id='bg',
            width=constants.canvas_width,
            height=constants.canvas_height,
            pos=(0, 0),
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
                    # print("exiting end day")
                    self.parent.endDayState = True
                    if self.parent.current_day >= 4:
                        self.parent.end_game=True
                    self.parent.is_choosing = False
                    # Restart the rightclick hint animation when returning to normal gameplay
                    if hasattr(self.parent, 'start_draw_card_hint_animation'):
                        self.parent.start_draw_card_hint_animation()
                    self.exit_state()
 
    def render(self, canvas):
        # for button in self.button _list:
        #         button.render(canvas)
        
        # utils.draw_rect(
        #     dest=canvas,
        #     size=(constants.canvas_width - 2*self.parent.box_width, constants.canvas_height),
        #     pos=(self.parent.box_width, 0),
        #     pos_anchor='topleft',
        #     color=(*colors.black, 90), # 50% transparency
        #     inner_border_width=0,
        #     outer_border_width=0,
        #     outer_border_color=colors.black
        # )
        
        # Title text
        utils.blit(dest=canvas, source=self.result_title, pos=(constants.canvas_width/2, constants.canvas_height/2 - 150), pos_anchor='center')
        if self.parent.current_day > 1:
            utils.blit(dest=canvas, source=self.vs_title, pos=(constants.canvas_width/2, constants.canvas_height/2 + 2), pos_anchor='center')
            if getattr(self.parent, f'final_day{self.parent.current_day}_score') <= getattr(self.parent, f'final_day{self.parent.current_day -1}_score'):
                utils.blit(dest=canvas, source=self.fail_title, pos=(constants.canvas_width/2, 515), pos_anchor='center')
                utils.blit(dest=canvas, source=self.fail_description, pos=(constants.canvas_width/2, 565), pos_anchor='center')
            else:
                utils.blit(dest=canvas, source=self.pass_title, pos=(constants.canvas_width/2, 515), pos_anchor='center')
                
        # Fruit and score
        if self.parent.current_day == 1:
            utils.blit(dest=canvas, source=self.result_surface_list[0]['surface_fruit'], pos=(constants.canvas_width/2 - 32, constants.canvas_height/2), pos_anchor='center')
            utils.blit(dest=canvas, source=self.result_surface_list[0]['surface'], pos=(constants.canvas_width/2 + 32, constants.canvas_height/2), pos_anchor='center')
        else:
            for i, option in enumerate(self.result_surface_list):
                utils.blit(dest=canvas, source=option['surface_fruit'], pos=(constants.canvas_width/2 - 32, 305 + i*120), pos_anchor='center')
                utils.blit(dest=canvas, source=option['surface'], pos=(constants.canvas_width/2 + 32, 305 + i*120), pos_anchor='center')
        
        # Continue text
        utils.blit(dest=canvas, source=self.continue_text, pos=(constants.canvas_width/2, 695), pos_anchor='center')
        