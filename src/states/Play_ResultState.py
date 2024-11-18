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
        self.setted_seed= not self.parent.set_seed
        sql_conn = sqlite3.connect('data/records.sqlite')
        sql_cursor = sql_conn.cursor()
        if self.setted_seed:
            # Check if seed exists
            sql_cursor.execute('SELECT COUNT(*) FROM records WHERE seed = ?', (self.parent.seed,))
            seed_exists = sql_cursor.fetchone()[0] > 0
            if not seed_exists:
                self.high_score = self.parent.total_score
            else:
                sql_cursor.execute('SELECT MAX(score) FROM records WHERE seed = ?', (self.parent.seed,))
                self.high_score = sql_cursor.fetchone()[0]
        else:
            sql_cursor.execute('SELECT COUNT(*) FROM records')
            records_exist = sql_cursor.fetchone()[0] > 0
            if not records_exist:
                self.high_score = self.parent.total_score
            else:
                sql_cursor.execute('SELECT MAX(score) FROM records')
                self.high_score = sql_cursor.fetchone()[0]
                
        sql_cursor.close()
        sql_conn.close()

        
        self.button_list = []
        
        self.final_results_text = utils.get_text(text='Final Results', font=fonts.lf2, size='large', color=colors.white)
        if self.setted_seed:
            self.seed_text = utils.get_text(text=f'Set Seed - {self.parent.seed}', font=fonts.lf2, size='medium', color=colors.white)
        elif not self.setted_seed:
            self.seed_text = utils.get_text(text=f'Random Seed', font=fonts.lf2, size='medium', color=colors.white)
            
        #self.seed_text = utils.get_text(text=f'Set Seed - {self.parent.seed}', font=fonts.lf2, size='medium', color=colors.white)
        
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
        
        
        self.day1_text = utils.get_text(text="Day 1", font=fonts.lf2, size='small', color=colors.white)
        self.day2_text = utils.get_text(text='Day 2', font=fonts.lf2, size='small', color=colors.white)
        self.day3_text = utils.get_text(text='Day 3', font=fonts.lf2, size='small', color=colors.white)
        self.day4_text = utils.get_text(text='Day 4', font=fonts.lf2, size='small', color=colors.white)
        self.seasonal_text = utils.get_text(text='Seasonal', font=fonts.lf2, size='small', color=colors.white)
        
        # Convert the score to string when calling get_text
        self.day1_score_text = utils.get_text(text=str(self.parent.final_day1_score),font=fonts.lf2,size='small', color=colors.white)
        self.day2_score_text = utils.get_text(text=str(self.parent.final_day2_score), font=fonts.lf2, size='small', color=colors.white)
        self.day3_score_text = utils.get_text(text=str(self.parent.final_day3_score), font=fonts.lf2, size='small', color=colors.white)
        self.day4_score_text = utils.get_text(text=str(self.parent.final_day4_score), font=fonts.lf2, size='small', color=colors.white)
        self.seasonal_score_text = utils.get_text(text=str(self.parent.final_seasonal_score), font=fonts.lf2, size='small', color=colors.white)
        
        self.total_text = utils.get_text(text='Total', font=fonts.lf2, size='small', color=colors.white)
        self.total_score_text = utils.get_text(text=str(self.parent.total_score), font=fonts.lf2, size='small', color=colors.white)
        
        self.high_score_text = utils.get_text(text='High Score', font=fonts.lf2, size='small', color=colors.white)
        self.high_score_fromDB_text = utils.get_text(text=str(self.high_score), font=fonts.lf2, size='small', color=colors.white)
        
        self.new_text=utils.get_text(text='New ', font=fonts.lf2, size='small', color=colors.green_medium)
        
        self.button_option_list = [
            {
                'id': 'continue',
                'text': 'Continue to main menu',
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
        if self.setted_seed:
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
                        self.parent.transitioning = True
                        self.game.music_channel.fadeout(1500)
                        utils.sound_play(sound=sfx.woop_in, volume=self.game.sfx_volume)
                        self.freeze_frame = self.game.canvas.copy()
                        def on_complete():
                            utils.music_load(music_channel=self.game.music_channel, name=music.menu_intro)
                            utils.music_queue(music_channel=self.game.music_channel, name=music.menu_loop, loops=-1)
                            self.game.music_channel.play()
                            self.parent.timer_manager.StopTimer(self.water_timer)
                            self.parent.tween_list.clear()
                            self.game.state_stack.clear()
                        self.parent.tween_list.append(tween.to(
                            container=self.parent,
                            key='mask_circle_radius',
                            end_value=0,
                            time=1,
                            ease_type=tweencurves.easeOutQuint
                        ).on_complete(on_complete))

            
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
  
            utils.blit(dest=canvas, source=self.glow_day1_fruit_image, pos=(constants.canvas_width/2 - 175, 150-10), pos_anchor=posanchors.topleft)
            utils.blit(dest=canvas, source=self.day1_text, pos=((constants.canvas_width/2 )-135, 140), pos_anchor=posanchors.topleft)
            utils.blit(dest=canvas, source=self.day1_score_text, pos=((constants.canvas_width/2 )+160, 140), pos_anchor=posanchors.topright)
            
            utils.blit(dest=canvas, source=self.glow_day2_fruit_image, pos=(constants.canvas_width/2 - 175, 210-10), pos_anchor=posanchors.topleft)
            utils.blit(dest=canvas, source=self.day2_text, pos=((constants.canvas_width/2 )-135, 200), pos_anchor=posanchors.topleft)
            utils.blit(dest=canvas, source=self.day2_score_text, pos=((constants.canvas_width/2 )+160, 200), pos_anchor=posanchors.topright)
            
            utils.blit(dest=canvas, source=self.glow_day3_fruit_image, pos=(constants.canvas_width/2 - 175, 270-10), pos_anchor=posanchors.topleft)
            utils.blit(dest=canvas, source=self.day3_text, pos=((constants.canvas_width/2 )-135, 260), pos_anchor=posanchors.topleft)
            utils.blit(dest=canvas, source=self.day3_score_text, pos=((constants.canvas_width/2 )+160, 260), pos_anchor=posanchors.topright)
            
            utils.blit(dest=canvas, source=self.glow_day4_fruit_image, pos=(constants.canvas_width/2 - 175, 330-10), pos_anchor=posanchors.topleft)
            utils.blit(dest=canvas, source=self.day4_text, pos=((constants.canvas_width/2 )-135, 320), pos_anchor=posanchors.topleft)
            utils.blit(dest=canvas, source=self.day4_score_text, pos=((constants.canvas_width/2 )+160, 320), pos_anchor=posanchors.topright)
            
            utils.blit(dest=canvas, source=self.glow_seasonal_fruit_image, pos=(constants.canvas_width/2 - 175, 390-10), pos_anchor=posanchors.topleft)
            utils.blit(dest=canvas, source=self.seasonal_text, pos=((constants.canvas_width/2 )-135, 380), pos_anchor=posanchors.topleft)
            utils.blit(dest=canvas, source=self.seasonal_score_text, pos=((constants.canvas_width/2 )+160, 380), pos_anchor=posanchors.topright)
            
            utils.blit(dest=canvas, source=self.total_text, pos=(constants.canvas_width/2 - 135, 440), pos_anchor=posanchors.topleft)
            utils.blit(dest=canvas, source=self.total_score_text, pos=((constants.canvas_width/2 )+160, 440), pos_anchor=posanchors.topright)
            
            utils.blit(dest=canvas, source=self.high_score_text ,pos=(constants.canvas_width/2 -135, 500), pos_anchor=posanchors.topleft)
            utils.blit(dest=canvas, source=self.high_score_fromDB_text, pos=((constants.canvas_width/2 )+160, 500), pos_anchor=posanchors.topright)
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