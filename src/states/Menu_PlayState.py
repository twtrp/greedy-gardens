from src.library.essentials import *
from src.template.BaseState import BaseState
from src.classes.Button import Button
from src.states.PlayState import PlayState

class Menu_PlayState(BaseState):
    def __init__(self, game, parent, stack):
        BaseState.__init__(self, game, parent, stack)

        self.button_list = []
        self.load_assets()


    #Main methods

    def load_assets(self):

        self.page_title = utils.get_text(text='Play', font=fonts.lf2, size='huge', color=colors.green_light)

        self.button_option_list = [
            {
                'id': 'start',
                'text': 'Start game',
            },
            {
                'id': 'back',
                'text': 'Back',
            }
        ]
        self.button_option_surface_list = []
        for option in self.button_option_list:
            text = utils.get_text(text=option['text'], font=fonts.lf2, size='medium', color=colors.white)
            self.button_option_surface_list.append({
                'id': option['id'],
                'surface': text,
                'scale': 1.0
            })
        for i, option in enumerate(self.button_option_surface_list):
            self.button_list.append(Button(game=self.game,
                                           id=option['id'],
                                           width=300,
                                           height=80,
                                           pos=(constants.canvas_width/2, 280 + i*300),
                                           pos_anchor='center'))
            
        self.textbox_label = utils.get_text(text='Seed', font=fonts.lf2, size='small', color=colors.white)
        self.textbox_mode = 'inactive'
        self.textbox_text = ''
        self.textbox_limit = 8
        self.textbox_text_surface = utils.get_text(text=self.textbox_text,
                                                   font=fonts.lf2,
                                                   size='small',
                                                   color=colors.mono_50,
                                                   long_shadow=False,
                                                   outline=False)

        self.textbox_placeholder_surface = utils.get_text(text='Random', font=fonts.lf2, size='small', color=colors.mono_100,
                                                  long_shadow=False, outline=False)
        self.button_list.append(Button(game=self.game,
                                       id='textbox',
                                       width=140,
                                       height=50,
                                       pos=(constants.canvas_width/2, 420),
                                       pos_anchor='center'))


    def update(self, dt, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.exit_state()

                if self.textbox_mode == 'active':
                    if event.key == pygame.K_BACKSPACE:
                        self.textbox_text = self.textbox_text[:-1]
                        self.textbox_text_surface = utils.get_text(text=self.textbox_text,
                                                                   font=fonts.lf2,
                                                                   size='small',
                                                                   color=colors.mono_50,
                                                                   long_shadow=False,
                                                                   outline=False)
                    elif event.key == pygame.K_RETURN:
                        self.textbox_mode = 'inactive'
                    else:
                        if len(self.textbox_text) < self.textbox_limit and event.unicode.isdigit():
                            self.textbox_text += event.unicode
                            self.textbox_text_surface = utils.get_text(text=self.textbox_text,
                                                                       font=fonts.lf2,
                                                                       size='small',
                                                                       color=colors.mono_50,
                                                                       long_shadow=False,
                                                                       outline=False)

            elif event.type == pygame.MOUSEBUTTONUP:
                if self.textbox_mode == 'active':
                    self.textbox_mode = 'inactive'

        for button in self.button_list:
            button.update(dt=dt, events=events)
            
            if button.hovered:
                self.cursor = button.hover_cursor
                for option in self.button_option_surface_list:
                    if button.id == option['id']:
                        option['scale'] = min(option['scale'] + 2.4*dt, 1.2)

                if button.id == 'textbox' and self.textbox_mode != 'active':
                    self.textbox_mode = 'hovered'

            else:
                for option in self.button_option_surface_list:
                    if button.id == option['id']:
                        option['scale'] = max(option['scale'] - 2.4*dt, 1.0)
                
                if button.id == 'textbox' and self.textbox_mode != 'active':
                    self.textbox_mode = 'inactive'
            
            if button.clicked:
                if button.id == 'start':
                    PlayState(game=self.game, parent=self.game, stack=self.game.state_stack, seed=self.textbox_text).enter_state()
                    self.exit_state()      
                elif button.id == 'textbox':
                    self.textbox_mode = 'active'            
                elif button.id == 'back':
                    self.exit_state()

        utils.set_cursor(cursor=self.cursor)
        self.cursor = cursors.normal


    def render(self, canvas):
        utils.blit(dest=canvas, source=self.page_title, pos=(constants.canvas_width/2, 120), pos_anchor='center')
        for i, option in enumerate(self.button_option_surface_list):
            processed_surface = pygame.transform.scale_by(surface=option['surface'], factor=option['scale'])
            utils.blit(dest=canvas, source=processed_surface, pos=(constants.canvas_width/2, 280 + i*300), pos_anchor='center')

        utils.blit(dest=canvas, source=self.textbox_label, pos=(constants.canvas_width/2, 373), pos_anchor='center')
        if self.textbox_mode == 'inactive':
            utils.draw_rect(dest=canvas,
                            size=(140, 50),
                            pos=(constants.canvas_width/2, 420), 
                            pos_anchor='center',
                            color=(*colors.white, 200),
                            inner_border_width=3)
            if self.textbox_text == '':
                utils.blit(dest=canvas, source=self.textbox_placeholder_surface, pos=(constants.canvas_width/2, 420), pos_anchor='center')
            else:
                utils.blit(dest=canvas, source=self.textbox_text_surface, pos=(constants.canvas_width/2, 420), pos_anchor='center')
        elif self.textbox_mode == 'hovered':
            utils.draw_rect(dest=canvas,
                            size=(140, 50),
                            pos=(constants.canvas_width/2, 420), 
                            pos_anchor='center',
                            color=(*colors.white, 200),
                            inner_border_width=3,
                            outer_border_width=3,
                            outer_border_color=colors.white)
            if self.textbox_text == '':
                utils.blit(dest=canvas, source=self.textbox_placeholder_surface, pos=(constants.canvas_width/2, 420), pos_anchor='center')
            else:
                utils.blit(dest=canvas, source=self.textbox_text_surface, pos=(constants.canvas_width/2, 420), pos_anchor='center')
        elif self.textbox_mode == 'active':
            utils.draw_rect(dest=canvas,
                            size=(140, 50),
                            pos=(constants.canvas_width/2, 420), 
                            pos_anchor='center',
                            color=(*colors.white, 200),
                            inner_border_width=3,
                            outer_border_width=3,
                            outer_border_color=colors.mono_175,
                            outest_border_width=3,
                            outest_border_color=colors.white)
            if self.textbox_text != '':
                utils.blit(dest=canvas, source=self.textbox_text_surface, pos=(constants.canvas_width/2, 420), pos_anchor='center')
            