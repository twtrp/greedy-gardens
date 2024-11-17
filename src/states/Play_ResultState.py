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
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT MAX(score) FROM scores')
        self.high_score = cursor.fetchone()[0] or 0
        conn.close()
        
        # Save current score to database
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO scores (score, seed, seed_type) VALUES (?, ?, ?)',
                    (self.parent.total_score, self.parent.seed, self.parent.seed_type))
        conn.commit()
        conn.close()

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
        self.high_score_value_text = utils.get_text(text=str(self.high_score), font=fonts.lf2, size='medium', color=colors.white)
        
        self.continue_button = Button(
            game=self.game,
            id='continue',
            text='Continue',
            font=fonts.lf2,
            size='medium',
            color=colors.yellow_medium,
            pos=(constants.canvas_width/2, constants.canvas_height - 200),
            pos_anchor='center',
            hover_cursor=cursors.hand,
        )
        self.button_list.append(self.continue_button)
        self.hover_text = utils.get_text(text='Hover here to view board', font=fonts.lf2, size='small', color=colors.white)

    def update(self, dt, events):
        for button in self.button_list:
            button.update(dt=dt, events=events)
            if button.hovered:
                if button.hover_cursor is not None:
                    self.cursor = button.hover_cursor

            if button.clicked:
                if button.id == 'continue':
                    print("End game")
                    #implement this to menu state
                    self.exit_state()

    def render(self, canvas):
        # Draw dark overlay when not hovering
        if self.is_hovering:
            utils.draw_rect(
                dest=canvas,
                size=(constants.canvas_width, constants.canvas_height),
                color=(0, 0, 0, 191),
            )
            
            # Render all result texts
            utils.blit(dest=canvas, source=self.final_results_text, 
                      pos=(constants.canvas_width/2, 50), pos_anchor='center')
            
            utils.blit(dest=canvas, source=self.seed_text,
                      pos=(constants.canvas_width/2, 100), pos_anchor='center')
            
            # Render day results
            for i in range(4):
                y_pos = 180 + i*60
                if self.day_fruits[i]:
                    utils.blit(dest=canvas, source=self.day_fruits[i],
                             pos=(constants.canvas_width/2 - 150, y_pos), pos_anchor='center')
                utils.blit(dest=canvas, source=self.day_texts[i],
                          pos=(constants.canvas_width/2, y_pos), pos_anchor='center')
                utils.blit(dest=canvas, source=self.day_scores[i],
                          pos=(constants.canvas_width/2 + 150, y_pos), pos_anchor='center')
            
            # Render total and high scores
            utils.blit(dest=canvas, source=self.total_text,
                      pos=(constants.canvas_width/2, 450), pos_anchor='center')
            utils.blit(dest=canvas, source=self.total_score_text,
                      pos=(constants.canvas_width/2 + 150, 450), pos_anchor='center')
            
            utils.blit(dest=canvas, source=self.high_score_text,
                      pos=(constants.canvas_width/2, 500), pos_anchor='center')
            utils.blit(dest=canvas, source=self.high_score_value_text,
                      pos=(constants.canvas_width/2 + 150, 500), pos_anchor='center')
            
            self.continue_button.render(canvas=canvas)

        # Always render hover text
        utils.blit(dest=canvas, source=self.hover_text,
                  pos=(constants.canvas_width/2, constants.canvas_height - 25), pos_anchor='center')
