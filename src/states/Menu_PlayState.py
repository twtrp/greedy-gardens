from src.library.essentials import *
from src.template.BaseState import BaseState
from src.classes.Button import Button
from src.states.PlayState import PlayState
from src.states.Menu_TutorialState import Menu_TutorialState

class Menu_PlayState(BaseState):
    def __init__(self, game, parent, stack):
        BaseState.__init__(self, game, parent, stack)

        self.button_list = []
        self.load_assets()

        self.transitioning = False
        self.freeze_frame = pygame.Surface(size=(constants.canvas_width, constants.canvas_height))

        self.mask_surface = pygame.Surface(size=(constants.canvas_width, constants.canvas_height), flags=pygame.SRCALPHA)
        self.mask_circle_radius = 750


    #Main methods

    def load_assets(self):

        self.page_title = utils.get_text(text='Play', font=fonts.boldpixels, size='large', color=colors.green_light)

        self.button_option_list = [
            {
                'id': 'start',
                'text': 'Start game',
            },
            {
                'id': 'tutorial',
                'text': 'How to play',
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
            if i != len(self.button_option_surface_list) - 1:
                self.button_list.append(Button(
                    game=self.game,
                    id=option['id'],
                    width=300,
                    height=70,
                    pos=(constants.canvas_width/2, 300 + i*70),
                    pos_anchor=posanchors.center
                ))
            else:
                self.button_list.append(Button(
                    game=self.game,
                    id=option['id'],
                    width=300,
                    height=80,
                    pos=(constants.canvas_width/2, 580),
                    pos_anchor=posanchors.center
                ))
        
            
        self.textbox_label = utils.get_text(text='Seed number', font=fonts.lf2, size='small', color=colors.mono_205)
        self.textbox_mode = 'inactive'
        self.textbox_text = ''
        self.textbox_limit = 6
        self.textbox_text_surface = utils.get_text(
            text=self.textbox_text,
            font=fonts.lf2,
            size='small',
            color=colors.mono_50,
            long_shadow=False,
            outline=False
        )

        self.textbox_placeholder_surface = utils.get_text(
            text='Random', font=fonts.lf2, size='small', color=colors.mono_100,
            long_shadow=False, outline=False
        )
        self.button_list.append(Button(
            game=self.game,
            id='textbox',
            width=140,
            height=50,
            pos=(constants.canvas_width/2, 490),
            pos_anchor=posanchors.center
        ))


    def update(self, dt, events):
        if not self.transitioning:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        utils.sound_play(sound=sfx.deselect, volume=self.game.sfx_volume)
                        self.exit_state()
                    if self.textbox_mode == 'active':
                        if event.key == pygame.K_BACKSPACE:
                            self.textbox_text = self.textbox_text[:-1]
                            self.textbox_text_surface = utils.get_text(
                                text=self.textbox_text,
                                font=fonts.lf2,
                                size='small',
                                color=colors.mono_50,
                                long_shadow=False,
                                outline=False
                            )
                            utils.sound_play(sound=sfx.keyboard, volume=self.game.sfx_volume, pitch_variation=0.2)
                        elif event.key == pygame.K_RETURN:
                            self.textbox_mode = 'inactive'
                        else:
                            if len(self.textbox_text) < self.textbox_limit and event.unicode.isdigit():
                                self.textbox_text += event.unicode
                                self.textbox_text_surface = utils.get_text(
                                    text=self.textbox_text,
                                    font=fonts.lf2,
                                    size='small',
                                    color=colors.mono_50,
                                    long_shadow=False,
                                    outline=False
                                )
                                utils.sound_play(sound=sfx.keyboard, volume=self.game.sfx_volume, pitch_variation=0.2)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 2:
                        utils.sound_play(sound=sfx.deselect, volume=self.game.sfx_volume)
                        self.exit_state()

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
                        self.game.music_channel.fadeout(1500)
                        utils.sound_play(sound=sfx.woop_in, volume=self.game.sfx_volume)
                        self.button_list.clear()
                        self.transitioning = True
                        self.freeze_frame = self.game.canvas.copy()
                        def on_complete():
                            self.parent.tween_list.clear()
                            PlayState(game=self.game, parent=self.game, stack=self.game.state_stack, seed=self.textbox_text).enter_state()
                        self.parent.tween_list.append(tween.to(
                            container=self,
                            key='mask_circle_radius',
                            end_value=0,
                            time=1,
                            ease_type=tweencurves.easeOutQuint
                        ).on_complete(on_complete))
                    elif button.id == 'tutorial':
                        utils.sound_play(sound=sfx.select, volume=self.game.sfx_volume)
                        Menu_TutorialState(game=self.game, parent=self.parent, stack=self.parent.substate_stack).enter_state()
                    elif button.id == 'textbox':
                        self.textbox_mode = 'active'            
                    elif button.id == 'back':
                        utils.sound_play(sound=sfx.deselect, volume=self.game.sfx_volume)
                        self.exit_state()

        utils.set_cursor(cursor=self.cursor)
        self.cursor = cursors.normal


    def render(self, canvas):
        if not self.transitioning:
            utils.blit(dest=canvas, source=self.page_title, pos=(constants.canvas_width/2, 120), pos_anchor=posanchors.center)
            for i, option in enumerate(self.button_option_surface_list):
                if i != len(self.button_option_surface_list) - 1:
                    processed_surface = pygame.transform.scale_by(surface=option['surface'], factor=option['scale'])
                    utils.blit(dest=canvas, source=processed_surface, pos=(constants.canvas_width/2, 300 + i*70), pos_anchor=posanchors.center)
                else:
                    processed_surface = pygame.transform.scale_by(surface=option['surface'], factor=option['scale'])
                    utils.blit(dest=canvas, source=processed_surface, pos=(constants.canvas_width/2, 580), pos_anchor=posanchors.center)

            utils.blit(dest=canvas, source=self.textbox_label, pos=(constants.canvas_width/2, 443), pos_anchor=posanchors.center)
            if self.textbox_mode == 'inactive':
                utils.draw_rect(
                    dest=canvas,
                    size=(140, 50),
                    pos=(constants.canvas_width/2, 490), 
                    pos_anchor=posanchors.center,
                    color=(*colors.white, 165),
                    inner_border_width=3
                )
                if self.textbox_text == '':
                    utils.blit(dest=canvas, source=self.textbox_placeholder_surface, pos=(constants.canvas_width/2, 490), pos_anchor=posanchors.center)
                else:
                    utils.blit(dest=canvas, source=self.textbox_text_surface, pos=(constants.canvas_width/2, 490), pos_anchor=posanchors.center)
            elif self.textbox_mode == 'hovered':
                utils.draw_rect(
                    dest=canvas,
                    size=(140, 50),
                    pos=(constants.canvas_width/2, 490), 
                    pos_anchor=posanchors.center,
                    color=(*colors.white, 165),
                    inner_border_width=3,
                    outer_border_width=3,
                    outer_border_color=colors.white
                )
                if self.textbox_text == '':
                    utils.blit(dest=canvas, source=self.textbox_placeholder_surface, pos=(constants.canvas_width/2, 490), pos_anchor=posanchors.center)
                else:
                    utils.blit(dest=canvas, source=self.textbox_text_surface, pos=(constants.canvas_width/2, 490), pos_anchor=posanchors.center)
            elif self.textbox_mode == 'active':
                utils.draw_rect(
                    dest=canvas,
                    size=(140, 50),
                    pos=(constants.canvas_width/2, 490), 
                    pos_anchor=posanchors.center,
                    color=(*colors.white, 165),
                    inner_border_width=3,
                    outer_border_width=3,
                    outer_border_color=colors.mono_175,
                    outest_border_width=3,
                    outest_border_color=colors.white
                )
                if self.textbox_text != '':
                    utils.blit(dest=canvas, source=self.textbox_text_surface, pos=(constants.canvas_width/2, 490), pos_anchor=posanchors.center)

        else:
            utils.blit(dest=canvas, source=self.freeze_frame)
            self.mask_surface.fill(color=colors.black)
            pygame.draw.circle(
                surface=self.mask_surface,
                color=(*colors.black, 0),
                center=(constants.canvas_width/2, constants.canvas_height/2),
                radius=self.mask_circle_radius
            )
            self.pixelated_mask_surface = utils.effect_pixelate(surface=self.mask_surface, pixel_size=4)
            utils.blit(dest=canvas, source=self.pixelated_mask_surface)

