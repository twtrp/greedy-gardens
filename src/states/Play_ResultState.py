from src.library.essentials import *
from src.template.BaseState import BaseState
from src.classes.Button import Button
import sqlite3

class Play_ResultStage(BaseState):
    def __init__(self, game, parent, stack):
        BaseState.__init__(self, game, parent, stack)

        # state
        self.is_hovering = False
        self.is_continue = False

        self.load_assets()
        

    def load_assets(self):
        
        self.new_record = False
        
        sql_conn = sqlite3.connect('data/records.sqlite')
        sql_cursor = sql_conn.cursor()
        if self.parent.set_seed:
            # Check if seed exists
            sql_cursor.execute('SELECT COUNT(*) FROM records WHERE seed = ?', (self.parent.seed,))
            seed_exists = sql_cursor.fetchone()[0] > 0
            if not seed_exists:
                self.high_score = 0
            else:
                sql_cursor.execute('SELECT MAX(score) FROM records WHERE seed = ?', (self.parent.seed,))
                self.high_score = sql_cursor.fetchone()[0]
        else:
            sql_cursor.execute('SELECT COUNT(*) FROM records')
            records_exist = sql_cursor.fetchone()[0] > 0
            if not records_exist:
                self.high_score = 0
            else:
                sql_cursor.execute('SELECT MAX(score) FROM records')
                self.high_score = sql_cursor.fetchone()[0]
                
        sql_cursor.close()
        sql_conn.close()

        
        self.button_list = []
        
        self.final_results_text = utils.get_text(text='Final Results', font=fonts.lf2, size='large', color=colors.white)
        if self.parent.set_seed:
            self.seed_text = utils.get_text(text=f'Set Seed - {self.parent.seed}', font=fonts.lf2, size='medium', color=colors.white)
        elif self.parent.set_seed:
            self.seed_text = utils.get_text(text=f'Random Seed', font=fonts.lf2, size='medium', color=colors.white)
            
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

        self.glow_day1_fruit_image = utils.effect_outline(surface=self.big_day1_fruit_image, distance=2, color=colors.white)
        self.glow_day2_fruit_image = utils.effect_outline(surface=self.big_day2_fruit_image, distance=2, color=colors.white)
        self.glow_day3_fruit_image = utils.effect_outline(surface=self.big_day3_fruit_image, distance=2, color=colors.white)
        self.glow_day4_fruit_image = utils.effect_outline(surface=self.big_day4_fruit_image, distance=2, color=colors.white)
        self.glow_seasonal_fruit_image = utils.effect_outline(surface=self.big_seasonal_fruit_image, distance=2, color=colors.white)
        
        
        self.day1_text = utils.get_text(text="Day 1", font=fonts.lf2, size='medium', color=colors.white)
        self.day2_text = utils.get_text(text='Day 2', font=fonts.lf2, size='medium', color=colors.white)
        self.day3_text = utils.get_text(text='Day 3', font=fonts.lf2, size='medium', color=colors.white)
        self.day4_text = utils.get_text(text='Day 4', font=fonts.lf2, size='medium', color=colors.white)
        self.seasonal_text = utils.get_text(text='Seasonal', font=fonts.lf2, size='medium', color=colors.white)
        
        # Convert the score to string when calling get_text
        self.day1_score_text = utils.get_text(text=str(self.parent.final_day1_score),font=fonts.lf2,size='small', color=colors.white)
        self.day2_score_text = utils.get_text(text=str(self.parent.final_day2_score), font=fonts.lf2, size='small', color=colors.white)
        self.day3_score_text = utils.get_text(text=str(self.parent.final_day3_score), font=fonts.lf2, size='small', color=colors.white)
        self.day4_score_text = utils.get_text(text=str(self.parent.final_day4_score), font=fonts.lf2, size='small', color=colors.white)
        self.seasonal_score_text = utils.get_text(text=str(self.parent.final_seasonal_score), font=fonts.lf2, size='small', color=colors.white)
        
        self.total_text = utils.get_text(text='Total', font=fonts.lf2, size='tiny', color=colors.white)
        self.total_score_text = utils.get_text(text=str(self.parent.total_score), font=fonts.lf2, size='small', color=colors.white)
        
        self.high_score_text = utils.get_text(text='High Score', font=fonts.lf2, size='tiny', color=colors.white)
        self.high_score_fromDB_text = utils.get_text(text=str(self.high_score), font=fonts.lf2, size='small', color=colors.white)
        
        self.new_text=utils.get_text(text='New ', font=fonts.lf2, size='tiny', color=colors.green_medium)
        
        self.button_option_list = [
            {
                'id': 'continue',
                'text': 'Continue',
                'size': 'medium',
                'color': colors.yellow_light,
            },
            {
                'id': 'view board',
                'text': 'Hover here to view board',
                'size': 'small',
                'color': colors.white,
            },
        ]
        self.button_option_surface_list = []
        for i, option in enumerate(self.button_option_list):
            text = utils.get_text(text=option['text'], font=fonts.lf2, size=option['size'], color=option['color'])
            self.button_option_surface_list.append({
                'id': option['id'],
                'surface': text,
                'scale': 1.0
            })
        self.button_list.append(Button(
            game=self.game,
            id=self.button_option_list[0]['id'],
            width=200,
            height=40,
            pos=(constants.canvas_width/2, 600),
            pos_anchor=posanchors.center
        ))
        self.button_list.append(Button(
            game=self.game,
            id=self.button_option_list[1]['id'],
            width=400,
            height=50,
            pos=(constants.canvas_width/2, 695),
            pos_anchor=posanchors.center,
            hover_cursor=cursors.hand,
        ))

        for button in self.button_list:
            print(button.id) 
        
        self.parent.endDayState=True
        
        sql_conn = sqlite3.connect('data/records.sqlite')
        sql_cursor = sql_conn.cursor()
        if self.parent.set_seed:
            sql_cursor.execute('SELECT MAX(score) FROM records WHERE seed = ?', (self.parent.seed,))
            result = sql_cursor.fetchone()
            current_high_score = result[0] if result[0] is not None else 0
            
            if self.parent.total_score > current_high_score:
                self.high_score = self.parent.total_score
                self.new_record = True
            else:
                self.high_score = current_high_score
                
            # Insert the new score
            sql_cursor.execute(
                'INSERT INTO records (score, seed, seed_type) VALUES (?, ?, ?)',
                (self.parent.total_score, self.parent.seed, 'Set Seed')
            )

        else:
            # Check highest score for random seeds
            sql_cursor.execute('SELECT MAX(score) FROM records WHERE seed_type = "Random Seed"')
            result = sql_cursor.fetchone()
            current_high_score = result[0] if result[0] is not None else 0
            
            if self.parent.total_score > current_high_score:
                self.high_score = self.parent.total_score
                self.new_record = True
            else:
                self.high_score = current_high_score
                
            # Insert the new score
            sql_cursor.execute(
                'INSERT INTO records (score, seed, seed_type) VALUES (?, ?, ?)',
                (self.parent.total_score, self.parent.seed, 'Random Seed')
            )

        sql_conn.commit()
        sql_cursor.close()
        sql_conn.close()
                

        
    def update(self, dt, events):
        if not self.is_continue:
            for button in self.button_list:
                button.update(dt=dt, events=events)
                if button.hovered:
                    if button.id == 'view board':
                        #print("Hovering over view board")
                        self.is_hovering = True
                    if button.hover_cursor is not None:
                        self.cursor = button.hover_cursor
                    for option in self.button_option_surface_list:
                        if button.id == option['id']:
                            option['scale'] = min(option['scale'] + 2.4*dt, 1.2)
                else: 
                    if button.id == 'view board':
                        # print("Hovering over other button")
                        self.is_hovering = False
                    for option in self.button_option_surface_list:
                        if button.id == option['id']:
                            option['scale'] = max(option['scale'] - 2.4*dt, 1.0)          
                if button.clicked:
                    for option in self.button_option_surface_list:
                        if button.id == 'continue':
                            self.is_continue = True
        else:
            print("End game")
            #implement this to menu state
            self.parent.exit_state()
            
        utils.set_cursor(cursor=self.cursor)
        self.cursor = cursors.normal

    def render(self, canvas):
        # For Rendering button hitboxes
        # for button in self.button_list:
        #     button.render(canvas=canvas)

        # Draw dark overlay when not hovering
        # print(self.is_hovering)
        if not self.is_hovering:
            utils.draw_rect(dest=canvas,
                        size=(constants.canvas_width, constants.canvas_height),
                        pos=(0, 0),
                        pos_anchor='topleft',
                        color=(*colors.black, 128), # 50% transparency
                        inner_border_width=0,
                        outer_border_width=0,
                        outer_border_color=colors.black)
            
            # Render all result texts
            utils.blit(dest=canvas, source=self.final_results_text,pos=(constants.canvas_width/2, 50), pos_anchor='center')
            
            utils.blit(dest=canvas, source=self.seed_text, pos=(constants.canvas_width/2, 100), pos_anchor='center')
  
            utils.blit(dest=canvas, source=self.glow_day1_fruit_image, pos=(constants.canvas_width/2 - 177, 150), pos_anchor=posanchors.topleft)
            utils.blit(dest=canvas, source=self.day1_text, pos=((constants.canvas_width/2 )-135, 140), pos_anchor=posanchors.topleft)
            utils.blit(dest=canvas, source=self.day1_score_text, pos=((constants.canvas_width/2 )+160, 140-10), pos_anchor=posanchors.topright)
            
            utils.blit(dest=canvas, source=self.glow_day2_fruit_image, pos=(constants.canvas_width/2 - 177, 210), pos_anchor=posanchors.topleft)
            utils.blit(dest=canvas, source=self.day2_text, pos=((constants.canvas_width/2 )-135, 200), pos_anchor=posanchors.topleft)
            utils.blit(dest=canvas, source=self.day2_score_text, pos=((constants.canvas_width/2 )+160, 200-10), pos_anchor=posanchors.topright)
            
            utils.blit(dest=canvas, source=self.glow_day3_fruit_image, pos=(constants.canvas_width/2 - 177, 270), pos_anchor=posanchors.topleft)
            utils.blit(dest=canvas, source=self.day3_text, pos=((constants.canvas_width/2 )-135, 260), pos_anchor=posanchors.topleft)
            utils.blit(dest=canvas, source=self.day3_score_text, pos=((constants.canvas_width/2 )+160, 260-10), pos_anchor=posanchors.topright)
            
            utils.blit(dest=canvas, source=self.glow_day4_fruit_image, pos=(constants.canvas_width/2 - 177, 330), pos_anchor=posanchors.topleft)
            utils.blit(dest=canvas, source=self.day4_text, pos=((constants.canvas_width/2 )-135, 320), pos_anchor=posanchors.topleft)
            utils.blit(dest=canvas, source=self.day4_score_text, pos=((constants.canvas_width/2 )+160, 320-10), pos_anchor=posanchors.topright)
            
            utils.blit(dest=canvas, source=self.glow_seasonal_fruit_image, pos=(constants.canvas_width/2 - 177, 390), pos_anchor=posanchors.topleft)
            utils.blit(dest=canvas, source=self.seasonal_text, pos=((constants.canvas_width/2 )-135, 380), pos_anchor=posanchors.topleft)
            utils.blit(dest=canvas, source=self.seasonal_score_text, pos=((constants.canvas_width/2 )+160, 380-10), pos_anchor=posanchors.topright)
            
            utils.blit(dest=canvas, source=self.total_text, pos=(constants.canvas_width/2 - 135, 440), pos_anchor=posanchors.topleft)
            utils.blit(dest=canvas, source=self.total_score_text, pos=((constants.canvas_width/2 )+160, 440-10), pos_anchor=posanchors.topright)
            
            utils.blit(dest=canvas, source=self.high_score_text ,pos=(constants.canvas_width/2 -135, 500), pos_anchor=posanchors.topleft)
            utils.blit(dest=canvas, source=self.high_score_fromDB_text, pos=((constants.canvas_width/2 )+160, 500-10), pos_anchor=posanchors.topright)
            if self.new_record:
                utils.blit(dest=canvas, source=self.new_text, pos=((constants.canvas_width/2 )-200, 500), pos_anchor=posanchors.topleft)
            # for i, option in enumerate(self.button_option_surface_list):
            #     if self.selected_cell or self.selected_cell_2:
            #         scaled_remove_button = pygame.transform.scale_by(surface=option['surface2'], factor=option['scale'])
            #     else:
            #         scaled_remove_button = pygame.transform.scale_by(surface=option['surface1'], factor=option['scale'])
            #     utils.blit(dest=canvas, source=scaled_remove_button, pos=(constants.canvas_width/2, 690), pos_anchor=posanchors.center)
            
            # Always render hoverable text
            scaled_continue_button = pygame.transform.scale_by(surface=self.button_option_surface_list[0]['surface'], factor=self.button_option_surface_list[0]['scale'])
            utils.blit(dest=canvas, source=scaled_continue_button, pos=(constants.canvas_width/2, 600), pos_anchor=posanchors.center)

            scaled_hover_to_button = pygame.transform.scale_by(surface=self.button_option_surface_list[1]['surface'], factor=self.button_option_surface_list[1]['scale'])
            utils.blit(dest=canvas, source=scaled_hover_to_button, pos=(constants.canvas_width/2, 695), pos_anchor=posanchors.center)
        else:
            pass