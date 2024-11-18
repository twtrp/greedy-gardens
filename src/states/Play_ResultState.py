from src.library.essentials import *
from src.template.BaseState import BaseState
from src.classes.Button import Button
import sqlite3

class Play_ResultStage(BaseState):
    def __init__(self, game, parent, stack):
        BaseState.__init__(self, game, parent, stack)
        self.parent = parent
        self.load_assets()
        
        # Get high score from database
        
        
        # Save current score to database
        #do later
        """conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO `records` (`score`, `seed`, `seed_type`) VALUES
                (50, 12345678, 'Set Seed'),
                (40, 23456789, 'Random Seed'),
                (30, 34567890, 'Random Seed'),
                (20, 45678901, 'Set Seed'),
                (10, 56789012, 'Random Seed'),
                (50, 23456789, 'Set Seed'),
                (60, 23456789, 'Set Seed') 
        ''')
        conn.commit()
        conn.close()"""

    def load_assets(self):
        
        sql_conn = sqlite3.connect('data/records.sqlite')
        sql_cursor = sql_conn.cursor()
        sql_cursor.execute('SELECT MAX(score) FROM records')
        self.high_score = sql_cursor.fetchall()[0][0]
        sql_cursor.close()
        #print(self.high_score)
        
        self.is_hovering=False
        self.button_list = []
        
        self.final_results_text = utils.get_text(text='Final Results', font=fonts.lf2, size='large', color=colors.white)
        if self.parent.set_seed:
            self.seed_text = utils.get_text(text=f'Set Seed - {self.parent.seed}', font=fonts.lf2, size='medium', color=colors.white)
        elif self.parent.set_seed:
            self.seed_text = utils.get_text(text=f'Random Seed - {self.parent.seed}', font=fonts.lf2, size='medium', color=colors.white)
            
        self.seed_text = utils.get_text(text=f'Set Seed - {self.parent.seed}', font=fonts.lf2, size='medium', color=colors.white)
        
        self.fruit_sprites = utils.get_sprite_sheet(sprite_sheet=spritesheets.fruit_16x16)
        #Gen chat and not work. Do later ()
        # Only scale images if they exist
        self.day1_fruit_color_image = self.fruit_sprites[self.parent.day1_fruit]
        self.day2_fruit_color_image = self.fruit_sprites[self.parent.day2_fruit]
        self.day3_fruit_color_image = self.fruit_sprites[self.parent.day3_fruit]
        self.day4_fruit_color_image = self.fruit_sprites[self.parent.day4_fruit]
        self.seasonal_fruit_color_image = self.fruit_sprites[self.parent.seasonal_fruit]
        
        self.big_day1_fruit_image = pygame.transform.scale_by(surface=self.day1_fruit_color_image, factor=2)
        self.big_day2_fruit_image = pygame.transform.scale_by(surface=self.day2_fruit_color_image, factor=2)
        self.big_day3_fruit_image = pygame.transform.scale_by(surface=self.day3_fruit_color_image, factor=2)
        self.big_day4_fruit_image = pygame.transform.scale_by(surface=self.day4_fruit_color_image, factor=2)
        self.big_seasonal_fruit_image = pygame.transform.scale_by(surface=self.seasonal_fruit_color_image, factor=2)
        
        self.day1_text = utils.get_text(text="Day 1", font=fonts.lf2, size='medium', color=colors.white)
        self.day2_text = utils.get_text(text='Day 2', font=fonts.lf2, size='medium', color=colors.white)
        self.day3_text = utils.get_text(text='Day 3', font=fonts.lf2, size='medium', color=colors.white)
        self.day4_text = utils.get_text(text='Day 4', font=fonts.lf2, size='medium', color=colors.white)
        self.seasonal_text = utils.get_text(text='Seasonal', font=fonts.lf2, size='medium', color=colors.white)
        
        # Convert the score to string when calling get_text
        self.day1_score_text = utils.get_text(text=str(self.parent.final_day1_score),font=fonts.lf2,size='medium', color=colors.white)
        self.day2_score_text = utils.get_text(text=str(self.parent.final_day2_score), font=fonts.lf2, size='medium', color=colors.white)
        self.day3_score_text = utils.get_text(text=str(self.parent.final_day3_score), font=fonts.lf2, size='medium', color=colors.white)
        self.day4_score_text = utils.get_text(text=str(self.parent.final_day4_score), font=fonts.lf2, size='medium', color=colors.white)
        self.seasonal_score_text = utils.get_text(text=str(self.parent.final_seasonal_score), font=fonts.lf2, size='medium', color=colors.white)
        
        self.total_text = utils.get_text(text='Total', font=fonts.lf2, size='medium', color=colors.white)
        self.total_score_text = utils.get_text(text=str(self.parent.total_score), font=fonts.lf2, size='medium', color=colors.white)
        
        self.high_score_text = utils.get_text(text='High Score', font=fonts.lf2, size='medium', color=colors.white)
        self.high_score_fromDB_text = utils.get_text(text=str(self.high_score), font=fonts.lf2, size='medium', color=colors.white)
        
        self.button_option_list = [
            {
                'id': 'continue',
                'text': 'Continue',
                'color1': colors.yellow_medium,
            }]
        self.button_option_surface_list = []
        for i, option in enumerate(self.button_option_list):
            text1 = utils.get_text(text=option['text'], font=fonts.lf2, size='medium', color=option['color1'])
            self.button_option_surface_list.append({
                'id': option['id'],
                'surface1': text1,
                'scale': 1.0
            })
            self.button_list.append(Button(
                game=self.game,
                id=option['id'],
                width=200,
                height=40,
                pos=(constants.canvas_width/2,600),
                pos_anchor=posanchors.center
            ))
        
        self.hover_to_view_title = utils.get_text(text='Hover here to view board', font=fonts.lf2, size='small', color=colors.white)
        self.hover_to_view_surface = [{
                    'id': 'view board',
                    'surface': self.hover_to_view_title,
                    'scale': 1.0,
                },]
        self.button_list.append(Button(
                    game=self.game,
                    id='view board',
                    width=400,
                    height=50,
                    pos=(constants.canvas_width/2, 695),
                    pos_anchor=posanchors.center
                ))
        self.parent.endDayState=True
        # First load the sprite sheet
        

        
    def update(self, dt, events):
        for button in self.button_list:
            button.update(dt=dt, events=events)
        for button in self.button_list:
            if button.hovered:
                if button.id == 'view board':
                    self.is_hovering = True
                # elif button.id == 'continue':
                #     for option in self.button_option_surface_list:
                #         if button.id == option['continue']:
                #             option['scale'] = min(option['scale'] + 2.4*dt, 1.2)
                #             option['scale_fruit'] = min(option['scale_fruit'] + 7.2*dt, 3.6)
                else:
                    self.is_hovering = False
                    
            elif button.clicked:
                if button.id == 'continue':
                    print("End game")
                    #implement this to menu state
                    self.exit_state()

    def render(self, canvas):
        for button in self.button_list:
            button.render(canvas=canvas)
        # Draw dark overlay when not hovering
        if not self.is_hovering:
            utils.draw_rect(dest=canvas,
                        size=(constants.canvas_width, constants.canvas_height),
                        pos=(self.parent.box_width, 0),
                        pos_anchor='topleft',
                        color=(*colors.black, 128), # 50% transparency
                        inner_border_width=0,
                        outer_border_width=0,
                        outer_border_color=colors.black)
            
            # Render all result texts
            utils.blit(dest=canvas, source=self.final_results_text,pos=(constants.canvas_width/2, 50), pos_anchor='center')
            
            utils.blit(dest=canvas, source=self.seed_text, pos=(constants.canvas_width/2, 100), pos_anchor='center')
  
            utils.blit(dest=canvas, source=self.big_day1_fruit_image, pos=(constants.canvas_width/2 - 175, 150), pos_anchor=posanchors.topleft)
            utils.blit(dest=canvas, source=self.day1_text, pos=((constants.canvas_width/2 )-135, 140), pos_anchor=posanchors.topleft)
            utils.blit(dest=canvas, source=self.day1_score_text, pos=((constants.canvas_width/2 )+130, 140), pos_anchor=posanchors.topright)
            
            utils.blit(dest=canvas, source=self.big_day2_fruit_image, pos=(constants.canvas_width/2 - 175, 210), pos_anchor=posanchors.topleft)
            utils.blit(dest=canvas, source=self.day2_text, pos=((constants.canvas_width/2 )-135, 200), pos_anchor=posanchors.topleft)
            utils.blit(dest=canvas, source=self.day2_score_text, pos=((constants.canvas_width/2 )+130, 200), pos_anchor=posanchors.topright)
            
            utils.blit(dest=canvas, source=self.big_day3_fruit_image, pos=(constants.canvas_width/2 - 175, 270), pos_anchor=posanchors.topleft)
            utils.blit(dest=canvas, source=self.day3_text, pos=((constants.canvas_width/2 )-135, 260), pos_anchor=posanchors.topleft)
            utils.blit(dest=canvas, source=self.day3_score_text, pos=((constants.canvas_width/2 )+130, 260), pos_anchor=posanchors.topright)
            
            utils.blit(dest=canvas, source=self.big_day4_fruit_image, pos=(constants.canvas_width/2 - 175, 330), pos_anchor=posanchors.topleft)
            utils.blit(dest=canvas, source=self.day4_text, pos=((constants.canvas_width/2 )-135, 320), pos_anchor=posanchors.topleft)
            utils.blit(dest=canvas, source=self.day4_score_text, pos=((constants.canvas_width/2 )+130, 320), pos_anchor=posanchors.topright)
            
            utils.blit(dest=canvas, source=self.big_seasonal_fruit_image, pos=(constants.canvas_width/2 - 175, 390), pos_anchor=posanchors.topleft)
            utils.blit(dest=canvas, source=self.seasonal_text, pos=((constants.canvas_width/2 )-135, 380), pos_anchor=posanchors.topleft)
            utils.blit(dest=canvas, source=self.seasonal_score_text, pos=((constants.canvas_width/2 )+130, 380), pos_anchor=posanchors.topright)
            
            utils.blit(dest=canvas, source=self.total_text, pos=(constants.canvas_width/2 - 135, 440), pos_anchor=posanchors.topleft)
            utils.blit(dest=canvas, source=self.total_score_text, pos=((constants.canvas_width/2 )+130, 440), pos_anchor=posanchors.topright)
            
            utils.blit(dest=canvas, source=self.high_score_text ,pos=(constants.canvas_width/2 -135, 500), pos_anchor=posanchors.topleft)
            utils.blit(dest=canvas, source=self.high_score_fromDB_text, pos=((constants.canvas_width/2 )+130, 500), pos_anchor=posanchors.topright)

            # for i, option in enumerate(self.button_option_surface_list):
            #     if self.selected_cell or self.selected_cell_2:
            #         scaled_remove_button = pygame.transform.scale_by(surface=option['surface2'], factor=option['scale'])
            #     else:
            #         scaled_remove_button = pygame.transform.scale_by(surface=option['surface1'], factor=option['scale'])
            #     utils.blit(dest=canvas, source=scaled_remove_button, pos=(constants.canvas_width/2, 690), pos_anchor=posanchors.center)
            
            # Always render hover text
            utils.blit(dest=canvas, source=self.hover_to_view_title ,pos=(constants.canvas_width/2, constants.canvas_height - 25), pos_anchor=posanchors.center)
        else:
            pass