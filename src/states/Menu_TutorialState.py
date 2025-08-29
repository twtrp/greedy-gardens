from src.library.essentials import *
from src.template.BaseState import BaseState
from src.classes.Button import Button
from src.states.PlayState import PlayState

class Menu_TutorialState(BaseState):
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
            pos=(constants.canvas_width/2, 660),
            pos_anchor=posanchors.center
        ))

        self.tutorial_coords_list = [
            (50, 40),
            (50, 210),
            (50, 420),
            (650, 40),
            (650, 210),
            (650, 380),
        ]

        self.tutorial_surface_list = [
            [
                utils.get_text(
                    text="Welcome to Greedy Gardens!",
                    font=fonts.minecraftia, size='medium', color=colors.green_light, long_shadow=False
                ),
                utils.get_text(
                    text="You're a fruit picker working on a 4-day contract.",
                    font=fonts.minecraftia, size='small', color=colors.white, long_shadow=False
                ),
                utils.get_text(
                    text="Your job is to collect fruits by building paths",
                    font=fonts.minecraftia, size='small', color=colors.white, long_shadow=False
                ),
                utils.get_text(
                    text="to connect fruits to the Farmhouse.",
                    font=fonts.minecraftia, size='small', color=colors.white, long_shadow=False
                ),
            ],
            [
                utils.get_text(
                    text="Be greedy, but not too much!",
                    font=fonts.minecraftia, size='medium', color=colors.yellow_light, long_shadow=False
                ),
                utils.get_text(
                    text="You must score more fruits than the previous day, or",
                    font=fonts.minecraftia, size='small', color=colors.white, long_shadow=False
                ),
                utils.get_text(
                    text="you will earn zero points for that day.",
                    font=fonts.minecraftia, size='small', color=colors.white, long_shadow=False
                ),
                utils.get_text(
                    text="Scoring too high can make the next day harder.",
                    font=fonts.minecraftia, size='small', color=colors.white, long_shadow=False
                ),
                utils.get_text(
                    text="Aim for the highest total score by the end of day 4.",
                    font=fonts.minecraftia, size='small', color=colors.white, long_shadow=False
                ),
            ],
            [
                utils.get_text(
                    text="All about fruits",
                    font=fonts.minecraftia, size='medium', color=colors.yellow_light, long_shadow=False
                ),
                utils.get_text(
                    text="Each day you can only score a specific fruit.",
                    font=fonts.minecraftia, size='small', color=colors.white, long_shadow=False
                ),
                utils.get_text(
                    text="You only know today's, tomorrow's, and seasonal fruit.",
                    font=fonts.minecraftia, size='small', color=colors.white, long_shadow=False
                ),
                utils.get_text(
                    text="Fruits connected to Farmhouse are scored when a day ends.",
                    font=fonts.minecraftia, size='small', color=colors.white, long_shadow=False
                ),
                utils.get_text(
                    text="Seasonal fruits are bonus points scored when the game ends.",
                    font=fonts.minecraftia, size='small', color=colors.white, long_shadow=False
                ),
            ],
            [
                utils.get_text(
                    text="All about paths",
                    font=fonts.minecraftia, size='medium', color=colors.yellow_light, long_shadow=False
                ),
                utils.get_text(
                    text="You can place paths based on the path cards you draw.",
                    font=fonts.minecraftia, size='small', color=colors.white, long_shadow=False
                ),
                utils.get_text(
                    text="Some cards path cards gives you a strike.",
                    font=fonts.minecraftia, size='small', color=colors.white, long_shadow=False
                ),
                utils.get_text(
                    text="After 3 strikes, the day ends.",
                    font=fonts.minecraftia, size='small', color=colors.white, long_shadow=False
                ),
            ],
            [
                utils.get_text(
                    text="All about events",
                    font=fonts.minecraftia, size='medium', color=colors.yellow_light, long_shadow=False
                ),
                utils.get_text(
                    text="Strikes from path cards will trigger events.",
                    font=fonts.minecraftia, size='small', color=colors.white, long_shadow=False
                ),
                utils.get_text(
                    text="Events can either help or ruin your plans.",
                    font=fonts.minecraftia, size='small', color=colors.white, long_shadow=False
                ),
                utils.get_text(
                    text="Each game has 16 event cards: 8 types with 2 of each.",
                    font=fonts.minecraftia, size='small', color=colors.white, long_shadow=False
                ),
            ],
            [
                utils.get_text(
                    text="All about magic fruits",
                    font=fonts.minecraftia, size='medium', color=colors.yellow_light, long_shadow=False
                ),
                utils.get_text(
                    text="There are 3 magic fruits on the board.",
                    font=fonts.minecraftia, size='small', color=colors.white, long_shadow=False
                ),
                utils.get_text(
                    text="Collecting a magic fruit will trigger an event assigned to it,",
                    font=fonts.minecraftia, size='small', color=colors.white, long_shadow=False
                ),
                utils.get_text(
                    text="as well as scoring 1 bonus point for that day.",
                    font=fonts.minecraftia, size='small', color=colors.white, long_shadow=False
                ),
            ],
        ]

        self.fruit_sprites = [
            utils.get_sprite(sprite_sheet=spritesheets.fruit_32x32, target_sprite='big_fruit_orange'),
            utils.get_sprite(sprite_sheet=spritesheets.fruit_32x32, target_sprite='big_fruit_blueberry'),
            utils.get_sprite(sprite_sheet=spritesheets.fruit_32x32, target_sprite='big_fruit_grape'),
            utils.get_sprite(sprite_sheet=spritesheets.fruit_32x32, target_sprite='big_fruit_strawberry'),
            utils.get_sprite(sprite_sheet=spritesheets.fruit_32x32, target_sprite='big_fruit_peach'),
            utils.get_sprite(sprite_sheet=spritesheets.fruit_32x32, target_sprite='big_fruit_coconut'),
        ]
        for i, surface in enumerate(self.fruit_sprites):
            self.fruit_sprites[i] = utils.effect_outline(surface=surface, distance=2, color=colors.mono_35)

        self.path_sprites = [
            utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='path_WE'),
            utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='path_NS'),
            utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='path_NW'),
            utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='path_NE'),
            utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='path_WS'),
            utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='path_ES'),
        ]
        for i, surface in enumerate(self.path_sprites):
            self.path_sprites[i] = pygame.transform.smoothscale_by(surface=surface, factor=0.75)
            self.path_sprites[i] = utils.effect_outline(surface=self.path_sprites[i], distance=2, color=colors.mono_35)

        self.event_sprites = [
            utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='event_free'),
            utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='event_move'),
            utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='event_merge'),
            utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='event_point'),
            utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='event_redraw'),
            utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='event_remove'),
            utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='event_reveal'),
            utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='event_swap'),
        ]
        for i, surface in enumerate(self.event_sprites):
            self.event_sprites[i] = pygame.transform.smoothscale_by(surface=surface, factor=0.75)
            self.event_sprites[i] = utils.effect_outline(surface=self.event_sprites[i], distance=2, color=colors.mono_35)

        self.magic_fruit_sprites = [
            utils.get_sprite(sprite_sheet=spritesheets.fruit_32x32, target_sprite='magic_fruit_1'),
            utils.get_sprite(sprite_sheet=spritesheets.fruit_32x32, target_sprite='magic_fruit_2'),
            utils.get_sprite(sprite_sheet=spritesheets.fruit_32x32, target_sprite='magic_fruit_3'),
        ]
        for i, surface in enumerate(self.magic_fruit_sprites):
            self.magic_fruit_sprites[i] = utils.effect_outline(surface=surface, distance=2, color=colors.mono_35)


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

        for i, group in enumerate(self.tutorial_surface_list):
            header_y_offset = -8
            y_increment = 0
            x, y = self.tutorial_coords_list[i]
            for text in group:
                utils.blit(
                    dest=canvas,
                    source=text,
                    pos=(x, y + header_y_offset + y_increment),
                    pos_anchor=posanchors.topleft
                )
                header_y_offset = 0
                y_increment += 40

        start_x = 280
        start_y = self.tutorial_coords_list[2][1] - 5
        x_increment = 40
        for i, surface in enumerate(self.fruit_sprites):
            utils.blit(
                dest=canvas, source=surface,
                pos=(start_x + i * x_increment, start_y),
                pos_anchor=posanchors.topleft
            )

        start_x = 880
        start_y = self.tutorial_coords_list[3][1] - 8
        x_increment = 40
        for i, surface in enumerate(self.path_sprites):
            utils.blit(
                dest=canvas, source=surface,
                pos=(start_x + i * x_increment, start_y),
                pos_anchor=posanchors.topleft
            )

        start_x = 895
        start_y = self.tutorial_coords_list[4][1] - 8
        x_increment = 40
        for i, surface in enumerate(self.event_sprites):
            utils.blit(
                dest=canvas, source=surface,
                pos=(start_x + i * x_increment, start_y),
                pos_anchor=posanchors.topleft
            )

        start_x = 965
        start_y = self.tutorial_coords_list[5][1] - 5
        x_increment = 40
        for i, surface in enumerate(self.magic_fruit_sprites):
            utils.blit(
                dest=canvas, source=surface,
                pos=(start_x + i * x_increment, start_y),
                pos_anchor=posanchors.topleft
            )