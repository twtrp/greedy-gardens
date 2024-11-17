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
        sql_conn = sqlite3.connect('data/records.sqlite')
        sql_cursor = sql_conn.cursor()
        sql_cursor.execute('SELECT MAX(score) FROM records')
        self.high_score = sql_cursor.fetchall()[0][0]
        sql_cursor.close()
        #print(self.high_score)
        
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
        self.is_hovering=False
        self.button_list = []
        
        self.final_results_text = utils.get_text(text='Final Results', font=fonts.lf2, size='large', color=colors.white)
        self.seed_text = utils.get_text(text=f'Set Seed - {self.parent.seed}', font=fonts.lf2, size='small', color=colors.white)
        
        self.day_texts = []
        self.day_scores = []
        self.day_fruits = []
        
        # Day 1-4 texts and scores
        for i in range(4):
            day_text = utils.get_text(text=f'Day {i+1}', font=fonts.lf2, size='medium', color=colors.white)
            self.day_texts.append(day_text)
            
            score = getattr(self.parent, f'final_day{i+1}_score')
            score_text = utils.get_text(text=str(score), font=fonts.lf2, size='medium', color=colors.white)
            self.day_scores.append(score_text)
            
            fruit = getattr(self.parent, f'day{i+1}_fruit')
            if fruit:
                fruit_image = self.parent.fruit_sprites[fruit]
                scaled_fruit = pygame.transform.scale_by(surface=fruit_image, factor=2)
                self.day_fruits.append(scaled_fruit)
            else:
                self.day_fruits.append(None)

        self.total_text = utils.get_text(text='Total', font=fonts.lf2, size='medium', color=colors.white)
        self.total_score_text = utils.get_text(text=str(self.parent.total_score), font=fonts.lf2, size='medium', color=colors.white)
        
        self.high_score_text = utils.get_text(text='High Score', font=fonts.lf2, size='medium', color=colors.white)
        #self.high_score_value_text = utils.get_text(text=str(self.high_score), font=fonts.lf2, size='medium', color=colors.white)
        
        """self.button_list.append(Button(
            game=self.game,
            id='continue',
            pos=(constants.canvas_width/2, constants.canvas_height - 200),
            pos_anchor=posanchors.center,
            enable_click=True,
            hover_cursor=cursors.hand,
        ))"""
        
        self.button_list.append(Button(
                    game=self.game,
                    id='view board',
                    width=400,
                    height=50,
                    pos=(constants.canvas_width/2, 695),
                    pos_anchor=posanchors.center
                ))
        
        self.hover_text = utils.get_text(text='Hover here to view board', font=fonts.lf2, size='small', color=colors.white)
        
        # First load the sprite sheet
        self.fruit_sprites = utils.get_sprite_sheet(sprite_sheet=spritesheets.fruit_16x16)
        #Gen chat and not work. Do later ()
        """# Only scale images if they exist
        if self.day1_fruit_image is not None:
            self.big_day1_fruit_image = pygame.transform.scale_by(surface=self.day1_fruit_image, factor=1.5)
        else:
            self.big_day1_fruit_image = None

        if self.day2_fruit_image is not None:
            self.big_day2_fruit_image = pygame.transform.scale_by(surface=self.day2_fruit_image, factor=1.5)
        else:
            self.big_day2_fruit_image = None

        if self.day3_fruit_image is not None:
            self.big_day3_fruit_image = pygame.transform.scale_by(surface=self.day3_fruit_image, factor=1.5)
        else:
            self.big_day3_fruit_image = None

        if self.day4_fruit_image is not None:
            self.big_day4_fruit_image = pygame.transform.scale_by(surface=self.day4_fruit_image, factor=1.5)
        else:
            self.big_day4_fruit_image = None"""

        
    def update(self, dt, events):
        for button in self.button_list:
            button.update(dt=dt, events=events)
            if button.hovered:
                if button.hover_cursor is not None:
                    self.cursor = button.hover_cursor
                if button.id == 'view board':
                    self.is_hovering = True
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
            utils.draw_rect(
                dest=canvas,
                size=(constants.canvas_width, constants.canvas_height),
                color=(0, 0, 0, 191),
            )
            
            # Render all result texts
            utils.blit(dest=canvas, source=self.final_results_text, 
                      pos=(constants.canvas_width/2, 50), pos_anchor=posanchors.center)
            
            utils.blit(dest=canvas, source=self.seed_text,
                      pos=(constants.canvas_width/2, 100), pos_anchor=posanchors.center)
            
            # Render day results
            for i in range(4):
                y_pos = 180 + i*60
                if self.day_fruits[i]:
                    utils.blit(dest=canvas, source=f'big_day{i+1}_fruit_image',
                             pos=(constants.canvas_width/2 - 150, y_pos), pos_anchor=posanchors.center)
                utils.blit(dest=canvas, source=self.day_texts[i],
                          pos=((constants.canvas_width/2 )-70, y_pos), pos_anchor=posanchors.center)
                utils.blit(dest=canvas, source=self.day_scores[i],
                          pos=(constants.canvas_width/2 + 150, y_pos), pos_anchor=posanchors.center)
            
            # Render total and high scores
            utils.blit(dest=canvas, source=self.total_text,
                      pos=(constants.canvas_width/2, 450), pos_anchor=posanchors.center)
            utils.blit(dest=canvas, source=self.total_score_text,
                      pos=(constants.canvas_width/2 + 150, 450), pos_anchor=posanchors.center)
            
            utils.blit(dest=canvas, source=self.high_score_text,
                      pos=(constants.canvas_width/2, 500),pos_anchor=posanchors.center)
            #utils.blit(dest=canvas, source=self.high_score_value_text,pos=(constants.canvas_width/2 + 150, 500), pos_anchor=posanchors.center)
            

        # Always render hover text
        utils.blit(dest=canvas, source=self.hover_text,
                  pos=(constants.canvas_width/2, constants.canvas_height - 25), pos_anchor=posanchors.center)
