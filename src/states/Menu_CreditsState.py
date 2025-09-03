from src.library.essentials import *
from src.template.BaseState import BaseState
from src.classes.Button import Button
from src.states.PlayState import PlayState

class Menu_CreditsState(BaseState):
    def __init__(self, game, parent, stack):
        BaseState.__init__(self, game, parent, stack)

        self.load_assets()


    #Main methods

    def load_assets(self):
        self.button_option_surface_list = []
        self.button_list = []
        self.button_option_surface_list.append({
            'id': 'back',
            'surface':  utils.get_text(text='Back', font=fonts.lf2, size='medium', color=colors.white),
            'scale': 1.0
        })
        self.button_list.append(Button(
            game=self.game,
            id='back',
            width=300,
            height=80,
            pos=(constants.canvas_width/2, 680),
            pos_anchor=posanchors.center
        ))


    def update(self, dt, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    utils.sound_play(sound=sfx.deselect, volume=self.game.sfx_volume)
                    self.exit_state()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 2:
                    utils.sound_play(sound=sfx.deselect, volume=self.game.sfx_volume)
                    self.exit_state()

        for button in self.button_list:
            button.update(dt=dt, events=events)
            
            if button.hovered:
                self.cursor = button.hover_cursor
                for option in self.button_option_surface_list:
                    if button.id == option['id']:
                        option['scale'] = min(option['scale'] + 2.4*dt, 1.2)
                        if button.clicked:
                            utils.sound_play(sound=sfx.deselect, volume=self.game.sfx_volume)
                            self.exit_state()
            else:
                for option in self.button_option_surface_list:
                    if button.id == option['id']:
                        option['scale'] = max(option['scale'] - 2.4*dt, 1.0)

        utils.set_cursor(cursor=self.cursor)
        self.cursor = cursors.normal


    def render(self, canvas):
        utils.draw_rect(
            dest=canvas,
            size=(constants.canvas_width - 40, constants.canvas_height - 100),
            pos=(20, 20),
            pos_anchor=posanchors.topleft,
            color=(*colors.mono_50, 225),
            inner_border_width=3
        )

        for i, option in enumerate(self.button_option_surface_list):
            processed_surface = pygame.transform.scale_by(surface=option['surface'], factor=option['scale'])
            utils.blit(dest=canvas, source=processed_surface, pos=(constants.canvas_width/2, 680), pos_anchor=posanchors.center)
