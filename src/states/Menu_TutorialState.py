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
                    font=fonts.minecraftia, size='medium', color=colors.green_light
                ),
                utils.get_text(
                    text="You're a fruit picker working on a 4 day contract.",
                    font=fonts.minecraftia, size='small', color=colors.white
                ),
                utils.get_text(
                    text="Your job is to collect fruits by building paths",
                    font=fonts.minecraftia, size='small', color=colors.white
                ),
                utils.get_text(
                    text="to connect fruits to the Farmhouse.",
                    font=fonts.minecraftia, size='small', color=colors.white
                ),
            ],
            [
                utils.get_text(
                    text="Balance your daily scores carefully!",
                    font=fonts.minecraftia, size='medium', color=colors.yellow_light
                ),
                utils.get_text(
                    text="You must score more fruits than the previous day, or",
                    font=fonts.minecraftia, size='small', color=colors.white
                ),
                utils.get_text(
                    text="you will earn zero points for that day.",
                    font=fonts.minecraftia, size='small', color=colors.white
                ),
                utils.get_text(
                    text="Scoring too high early can make the next day harder.",
                    font=fonts.minecraftia, size='small', color=colors.white
                ),
                utils.get_text(
                    text="Aim for the highest total score by the end of day 4.",
                    font=fonts.minecraftia, size='small', color=colors.white
                ),
            ],
            [
                utils.get_text(
                    text="All about fruits",
                    font=fonts.minecraftia, size='medium', color=colors.yellow_light
                ),
                utils.get_text(
                    text="Each day you can only score a specific fruit.",
                    font=fonts.minecraftia, size='small', color=colors.white
                ),
                utils.get_text(
                    text="You only know today's, tomorrow's, and seasonal fruit.",
                    font=fonts.minecraftia, size='small', color=colors.white
                ),
                utils.get_text(
                    text="Fruits connected to Farmhouse are scored when a day ends.",
                    font=fonts.minecraftia, size='small', color=colors.white
                ),
                utils.get_text(
                    text="Seasonal fruits are bonus objectives scored when the game ends.",
                    font=fonts.minecraftia, size='small', color=colors.white
                ),
            ],
            [
                utils.get_text(
                    text="All about paths:",
                    font=fonts.minecraftia, size='medium', color=colors.yellow_light
                ),
                utils.get_text(
                    text="You can place paths based on the path cards you draw.",
                    font=fonts.minecraftia, size='small', color=colors.white
                ),
                utils.get_text(
                    text="Some cards path cards gives you a strike.",
                    font=fonts.minecraftia, size='small', color=colors.white
                ),
                utils.get_text(
                    text="After 3 strikes, the day ends.",
                    font=fonts.minecraftia, size='small', color=colors.white
                ),
            ],
            [
                utils.get_text(
                    text="All about events:",
                    font=fonts.minecraftia, size='medium', color=colors.yellow_light
                ),
                utils.get_text(
                    text="Strikes from path cards will trigger events.",
                    font=fonts.minecraftia, size='small', color=colors.white
                ),
                utils.get_text(
                    text="Every event can either help or disrupt your plans.",
                    font=fonts.minecraftia, size='small', color=colors.white
                ),
                utils.get_text(
                    text="Each game has 16 event cards: 8 types with 2 of each.",
                    font=fonts.minecraftia, size='small', color=colors.white
                ),
            ],
            [
                utils.get_text(
                    text="All about magic fruits:",
                    font=fonts.minecraftia, size='medium', color=colors.yellow_light
                ),
                utils.get_text(
                    text="There are 3 magic fruits on the board.",
                    font=fonts.minecraftia, size='small', color=colors.white
                ),
                utils.get_text(
                    text="Collecting a Magic Fruit will trigger an event assigned to it,",
                    font=fonts.minecraftia, size='small', color=colors.white
                ),
                utils.get_text(
                    text="and well as providing 1 bonus score for that day.",
                    font=fonts.minecraftia, size='small', color=colors.white
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


    def update(self, dt, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
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
            color=(*colors.mono_50, 165),
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

        # start_x = 280
        # start_y = 415
        # x_increment = 40
        # for i, surface in enumerate(self.fruit_sprites):
        #     utils.blit(
        #         dest=canvas, source=surface,
        #         pos=(start_x + i * x_increment, start_y),
        #         pos_anchor=posanchors.topleft
        #     )