from src.library.essentials import *
from src.template.BaseState import BaseState
from src.classes.Wind import Wind
from src.states.MenuState import MenuState
from src.classes.Button import Button
from src.states.Tutorial_PlayState import Tutorial_PlayState

class TutorialState(BaseState):
    def __init__(self, game, parent, stack, finished_bootup=False):
        BaseState.__init__(self, game, parent, stack, finished_bootup)

        self.substate_stack = []

        self.ready = False
        self.finished_boot_up = finished_bootup
        self.finished_tween = False
        self.load_assets()

        self.tween_list = []
        if not self.finished_boot_up:
            skip_bootup = debug.debug_skip_bootup or self.game.settings['skip_bootup']
            self.bootup_tween_chain(skip=skip_bootup)
            self.transitioning = False
        else:
            self.bootup_tween_chain(skip=True)
            utils.sound_play(sound=sfx.woop_out, volume=self.game.sfx_volume)
            def on_complete():
                self.transitioning = False
                self.tween_list.clear()
            self.transitioning = True
            self.mask_surface = pygame.Surface(size=(constants.canvas_width, constants.canvas_height), flags=pygame.SRCALPHA)
            self.mask_circle_radius = 0
            self.tween_list.append(tween.to(
                container=self,
                key='mask_circle_radius',
                end_value=750,
                time=1,
                ease_type=tweencurves.easeInQuint
            ).on_complete(on_complete))

        self.ready = True


    #Main methods

    def load_assets(self):
        # Load white overlay
        self.overlay = pygame.Surface(size=(constants.canvas_width, constants.canvas_height), flags=pygame.SRCALPHA)
        self.overlay_props = {'alpha': 255}
        self.overlay.fill(color=(*colors.white, self.overlay_props['alpha']))
        
        # Load intro assets
        self.surface_logo = pygame.Surface(size=(constants.canvas_width, constants.canvas_height), flags=pygame.SRCALPHA)
        self.surface_logo_props = {'y_offset': 0, 'alpha': 0, 'scale': 0.7}

        self.team_namsom_logo = utils.get_image(dir=dir.branding, name='team_namsom_logo.png', mode='colorkey')
        self.team_namsom_logo = pygame.transform.scale_by(surface=self.team_namsom_logo, factor=5)
        utils.blit(
            dest=self.surface_logo,
            source=self.team_namsom_logo,
            pos=(self.surface_logo.get_width()/2 - 70, self.surface_logo.get_height()/2),
            pos_anchor=posanchors.midright,
        )

        self.my_logo = utils.get_image(dir=dir.branding, name='ttewtor_logo.png', mode='colorkey')
        self.my_logo = pygame.transform.scale_by(surface=self.my_logo, factor=2)
        utils.blit(
            dest=self.surface_logo,
            source=self.my_logo,
            pos=(self.surface_logo.get_width()/2 + 10, self.surface_logo.get_height()/2),
            pos_anchor=posanchors.midleft,
        )

        # Load menu background assets
        self.sky = utils.get_image(dir=dir.menu_bg, name='1_sky.png', mode='colorkey')
        self.parallax_list = [
            {
                'image': utils.get_image(dir=dir.menu_bg, name='2_cloud_1.png', mode='colorkey'),
                'x_offset': 0,
                'x_step': 0.5,
            },
            {
                'image': utils.get_image(dir=dir.menu_bg, name='3_cloud_2.png', mode='colorkey'),
                'x_offset': 0,
                'x_step': 2.5,
            },
            {
                'image': utils.get_image(dir=dir.menu_bg, name='4_cloud_3.png', mode='colorkey'),
                'x_offset': 0,
                'x_step': 7,
            },
        ]
        self.landscape_list = [
            {
                'image': utils.get_image(dir=dir.menu_bg, name='5_landscape_1.png', mode='colorkey'),
                'y_offset': 200,
            },
            {
                'image': utils.get_image(dir=dir.menu_bg, name='6_landscape_2.png', mode='colorkey'),
                'y_offset': 400,
            },
            {
                'image': utils.get_image(dir=dir.menu_bg, name='7_landscape_3.png', mode='colorkey'),
                'y_offset': 1000,
            },
        ]

        self.wind_entities_list = []
        self.winds_props = {'y_offset': 1000}
        self.wind_spawn_rate_per_second = 0.85
        self.wind_sprites = utils.get_sprite_sheet(sprite_sheet=spritesheets.wind, mode='alpha')
        for wind_sprite in self.wind_sprites:
            self.wind_sprites[wind_sprite] = pygame.transform.scale_by(self.wind_sprites[wind_sprite], (4, 2))

        # Initiate menu background surface
        self.menu_bg = pygame.Surface(size=(constants.canvas_width, constants.canvas_height))
        self.menu_bg_pixel_size = 2

        # Load mask
        self.mask_surface = pygame.Surface(size=(constants.canvas_width, constants.canvas_height), flags=pygame.SRCALPHA)
        self.mask_circle_radius = 750

        # Load content 
        self.welcome_text = utils.get_text(
            text='Welcome to',
            font=fonts.wacky_pixels,
            size='large',
            color=colors.white,
        )
        self.welcome_text_props = {
            'pos': (constants.canvas_width/2, 120),
            'pos_anchor': posanchors.center,
            'scale': 0.5,
            'alpha': 0
        }

        self.game_logo = utils.get_image(dir=dir.branding, name='game_logo.png', mode='colorkey')
        self.game_logo = pygame.transform.scale_by(surface=self.game_logo, factor=4)
        self.game_logo_props = {
            'pos': (constants.canvas_width/2, 270),
            'pos_anchor': posanchors.center,
            'scale': 0.5,
            'alpha': 0
        }

        self.question_text = utils.get_text(
            text='Do you want to learn how to play?',
            font=fonts.wacky_pixels,
            size='small',
            color=colors.white,
        )
        self.question_text_2 = utils.get_text(
            text='You can access the tutorial later.',
            font=fonts.wacky_pixels,
            size='small',
            color=colors.white,
        )
        self.question_text_surface = pygame.Surface(
            size=(max(self.question_text.get_width(), self.question_text_2.get_width()), self.question_text.get_height()*1.5 + self.question_text_2.get_height()),
            flags=pygame.SRCALPHA
        )
        utils.blit(
            dest=self.question_text_surface,
            source=self.question_text,
            pos=(self.question_text_surface.get_width()/2, self.question_text.get_height()/2),
            pos_anchor=posanchors.midtop
        )
        utils.blit(
            dest=self.question_text_surface,
            source=self.question_text_2,
            pos=(self.question_text_surface.get_width()/2, self.question_text.get_height() + self.question_text_2.get_height()/2),
            pos_anchor=posanchors.midtop
        )
        self.question_text_props = {
            'pos': (constants.canvas_width/2, 450),
            'pos_anchor': posanchors.center,
            'scale': 0.5,
            'alpha': 0
        }

        self.no_button_symbol = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='wrong', mode='colorkey')
        self.no_button_text = utils.get_text(
            text='Skip',
            font=fonts.lf2,
            size='medium',
        )
        self.no_button_surface = pygame.Surface(
            size=(
                self.no_button_symbol.get_width() + self.no_button_text.get_width() + 8,
                max(self.no_button_symbol.get_height(), self.no_button_text.get_height())
            ),
            flags=pygame.SRCALPHA
        )
        utils.blit(
            dest=self.no_button_surface,
            source=self.no_button_symbol,
            pos=(0, self.no_button_surface.get_height()/2),
            pos_anchor=posanchors.midleft
        )
        utils.blit(
            dest=self.no_button_surface,
            source=self.no_button_text,
            pos=(self.no_button_symbol.get_width() + 8, self.no_button_surface.get_height()/2),
            pos_anchor=posanchors.midleft
        )
        self.no_button_props = {
            'pos': (constants.canvas_width/2 - 120, 580),
            'pos_anchor': posanchors.center,
            'scale': 0.5,
            'alpha': 0,
        }

        self.yes_button_symbol = utils.get_sprite(sprite_sheet=spritesheets.gui, target_sprite='correct', mode='colorkey')
        self.yes_button_text = utils.get_text(
            text='Yes',
            font=fonts.lf2,
            size='medium',
        )
        self.yes_button_surface = pygame.Surface(
            size=(
                self.yes_button_symbol.get_width() + self.yes_button_text.get_width() + 8,
                max(self.yes_button_symbol.get_height(), self.yes_button_text.get_height())
            ),
            flags=pygame.SRCALPHA
        )
        utils.blit(
            dest=self.yes_button_surface,
            source=self.yes_button_symbol,
            pos=(0, self.yes_button_surface.get_height()/2),
            pos_anchor=posanchors.midleft
        )
        utils.blit(
            dest=self.yes_button_surface,
            source=self.yes_button_text,
            pos=(self.yes_button_symbol.get_width() + 8, self.yes_button_surface.get_height()/2),
            pos_anchor=posanchors.midleft
        )
        self.yes_button_props = {
            'pos': (constants.canvas_width/2 + 100, 580),
            'pos_anchor': posanchors.center,
            'scale': 0.5,
            'alpha': 0,
        }

        # Load buttons
        self.button_list = []
        self.button_list.append(Button(
            game=self.game,
            id='no',
            surface=self.no_button_surface,
            pos=self.no_button_props['pos'],
            pos_anchor=self.no_button_props['pos_anchor'],
            padding_x = 20,
            padding_y = 20,
        ))
        self.button_list.append(Button(
            game=self.game,
            id='yes',
            surface=self.yes_button_surface,
            pos=self.yes_button_props['pos'],
            pos_anchor=self.yes_button_props['pos_anchor'],
            padding_x = 20,
            padding_y = 20,
        ))

        self.button_surface_list = []
        self.button_surface_list.append({
            'id': 'no',
            'surface': self.no_button_surface,
            'pos': self.no_button_props['pos'],
            'pos_anchor': self.no_button_props['pos_anchor'],
            'scale': 1.0,
        })
        self.button_surface_list.append({
            'id': 'yes',
            'surface': self.yes_button_surface,
            'pos': self.yes_button_props['pos'],
            'pos_anchor': self.yes_button_props['pos_anchor'],
            'scale': 1.0,
        })

    def update(self, dt, events):
        if self.ready:

            # Update substates
            if self.substate_stack:
                self.substate_stack[-1].update(dt=dt, events=events)

            # Update tweens
            tween.update(passed_time=dt)

            # Update parallax
            for layer in self.parallax_list:
                layer['x_offset'] -= layer['x_step']*self.menu_bg_pixel_size*dt
                if abs(layer['x_offset']) > layer['image'].get_width():
                    layer['x_offset'] = 0

            # Update winds
            for wind in self.wind_entities_list:
                wind.update_y_offset(y_offset=self.winds_props['y_offset'])
                if wind.active:
                    wind.update(dt=dt, events=[])
                else:
                    self.wind_entities_list.remove(wind)

            spawn_rate = self.wind_spawn_rate_per_second * dt
            spawns = int(spawn_rate)
            spawn_chance = spawn_rate - spawns
            for _ in range(spawns):
                self.wind_entities_list.append(Wind(surface=self.menu_bg, sprites=self.wind_sprites))

            if random.random() <= spawn_chance:
                self.wind_entities_list.append(Wind(surface=self.menu_bg, sprites=self.wind_sprites))

            # Update buttons
            if self.finished_tween:
                for button in self.button_list:
                    button.update(dt=dt, events=events)
                    
                    if button.hovered:
                        self.cursor = button.hover_cursor
                        for option in self.button_surface_list:
                            if button.id == option['id']:
                                option['scale'] = min(option['scale'] + 2.4*dt, 1.2)
                        
                        if button.clicked:
                            if button.id == 'yes':
                                self.game.music_channel.fadeout(1500)
                                utils.sound_play(sound=sfx.woop_in, volume=self.game.sfx_volume)
                                self.button_list.clear()
                                self.transitioning = True
                                self.freeze_frame = self.game.canvas.copy()
                                def on_complete():
                                    self.tween_list.clear()
                                    Tutorial_PlayState(game=self.game, parent=self.game, stack=self.game.state_stack, seed=878495).enter_state()
                                self.tween_list.append(tween.to(
                                    container=self,
                                    key='mask_circle_radius',
                                    end_value=0,
                                    time=1,
                                    ease_type=tweencurves.easeOutQuint
                                ).on_complete(on_complete))
                    else:
                        for option in self.button_surface_list:
                            if button.id == option['id']:
                                option['scale'] = max(option['scale'] - 2.4*dt, 1.0)

        utils.set_cursor(cursor=self.cursor)
        self.cursor = cursors.normal


    def render(self, canvas):
        if self.ready:

            for button in self.button_list: 
                button.render(canvas)

            # Build background

            ## Render sky to menu_bg
            utils.blit(dest=self.menu_bg, source=self.sky)

            ## Render parallax to menu_bg
            for layer in self.parallax_list:
                num_duplicates = math.ceil(constants.canvas_width/layer['image'].get_width()) + 1
                for i in range(num_duplicates):
                    utils.blit(dest=self.menu_bg, source=layer['image'], pos=(layer['image'].get_width()*i + layer['x_offset'], 0))

            ## Render landscape to menu_bg
            for layer in self.landscape_list:
                utils.blit(dest=self.menu_bg, source=layer['image'], pos=(0, layer['y_offset']))

            ## Render winds to menu_bg
            for wind in self.wind_entities_list:
                wind.render()

            ## Render final menu_bg to canvas
            utils.blit(dest=canvas, source=utils.effect_pixelate(surface=self.menu_bg, pixel_size=self.menu_bg_pixel_size))


            # Build intro

            ## Render overlay
            if hasattr(self, 'overlay'):
                processed_overlay = self.overlay.copy()
                processed_overlay.set_alpha(self.overlay_props['alpha'])
                utils.blit(dest=canvas, source=processed_overlay)

            ## Render logo
            if hasattr(self, 'surface_logo'):
                processed_surface_logo = pygame.transform.smoothscale_by(surface=self.surface_logo, factor=self.surface_logo_props['scale'])
                processed_surface_logo.set_alpha(self.surface_logo_props['alpha'])
                utils.blit(
                    dest=canvas,
                    source=processed_surface_logo,
                    pos=(constants.canvas_width/2, constants.canvas_height/2 - 20 + self.surface_logo_props['y_offset']),
                    pos_anchor=posanchors.center,
                )
                
            # Render substates

            if not self.substate_stack:
                ## Render welcome text
                processed_welcome_text = pygame.transform.scale_by(surface=self.welcome_text, factor=self.welcome_text_props['scale'])
                processed_welcome_text.set_alpha(self.welcome_text_props['alpha'])
                utils.blit(dest=canvas, source=processed_welcome_text, pos=self.welcome_text_props['pos'], pos_anchor=self.welcome_text_props['pos_anchor'])

                ## Render game logo
                processed_game_logo = pygame.transform.scale_by(surface=self.game_logo, factor=self.game_logo_props['scale'])
                processed_game_logo.set_alpha(self.game_logo_props['alpha'])
                utils.blit(dest=canvas, source=processed_game_logo, pos=self.game_logo_props['pos'], pos_anchor=self.welcome_text_props['pos_anchor'])

                ## Render question text
                processed_question_text = pygame.transform.scale_by(surface=self.question_text_surface, factor=self.question_text_props['scale'])
                processed_question_text.set_alpha(self.question_text_props['alpha'])
                utils.blit(dest=canvas, source=processed_question_text, pos=self.question_text_props['pos'], pos_anchor=self.question_text_props['pos_anchor'])

                ## Render buttons
                if not self.finished_tween:
                    processed_no_button = pygame.transform.scale_by(surface=self.no_button_surface, factor=self.no_button_props['scale'])
                    processed_no_button.set_alpha(self.no_button_props['alpha'])
                    utils.blit(dest=canvas, source=processed_no_button, pos=self.no_button_props['pos'], pos_anchor=self.no_button_props['pos_anchor'])

                    processed_yes_button = pygame.transform.scale_by(surface=self.yes_button_surface, factor=self.yes_button_props['scale'])
                    processed_yes_button.set_alpha(self.yes_button_props['alpha'])
                    utils.blit(dest=canvas, source=processed_yes_button, pos=self.yes_button_props['pos'], pos_anchor=self.yes_button_props['pos_anchor'])
                else:
                    for option in self.button_surface_list:
                        processed_button = pygame.transform.scale_by(surface=option['surface'], factor=option['scale'])
                        utils.blit(dest=canvas, source=processed_button, pos=option['pos'], pos_anchor=option['pos_anchor'])
                
            else:
                self.substate_stack[-1].render(canvas=canvas)


        if self.transitioning:
            # transition mask     
            self.mask_surface.fill(color=colors.black)
            pygame.draw.circle(
                surface=self.mask_surface,
                color=(*colors.black, 0),
                center=(constants.canvas_width/2, constants.canvas_height/2),
                radius=self.mask_circle_radius
            )
            self.pixelated_mask_surface = utils.effect_pixelate(surface=self.mask_surface, pixel_size=4)
            utils.blit(dest=canvas, source=self.pixelated_mask_surface)



    #Class methods
  
    def bootup_tween_chain(self, skip=False):
        if not skip:
            delay = 0
            self.tween_list.append(tween.to(
                container=self.surface_logo_props,
                key='alpha',
                end_value=255,
                time=2,
                ease_type=tweencurves.easeOutCubic,
                delay=delay
            ))
            self.tween_list.append(tween.to(
                container=self.surface_logo_props,
                key='scale',
                end_value=1,
                time=3,
                ease_type=tweencurves.easeOutCubic,
                delay=delay
            ))

            delay += 2
            self.tween_list.append(tween.to(
                container=self.overlay_props,
                key='alpha',
                end_value=0,
                time=2,
                ease_type=tweencurves.easeOutQuad,
                delay=delay
            ))
            for layer in self.landscape_list:
                self.tween_list.append(tween.to(
                    container=layer,
                    key='y_offset',
                    end_value=0,
                    time=3,
                    ease_type=tweencurves.easeOutQuint,
                    delay=delay
                ))
                
            self.tween_list.append(tween.to(
                container=self.winds_props,
                key='y_offset',
                end_value=0,
                time=3,
                ease_type=tweencurves.easeOutQuint,
                delay=delay
            ))
            self.tween_list.append(tween.to(
                container=self.surface_logo_props,
                key='y_offset',
                end_value=-500,
                time=3,
                ease_type=tweencurves.easeOutQuart,
                delay=delay
            ).on_complete(self.finish_bootup))
            
            delay += 1.85   
            def start_music():
                utils.music_load(music_channel=self.game.music_channel, name=music.menu_intro)
                utils.music_queue(music_channel=self.game.music_channel, name=music.menu_loop, loops=-1)
                self.game.music_channel.play()    
            self.tween_list.append(tween.to(
                container=self.welcome_text_props,
                key='scale',
                end_value=1,
                time=0.75,
                ease_type=tweencurves.easeOutElastic,
                delay=delay
            ).on_start(start_music))
            self.tween_list.append(tween.to(
                container=self.welcome_text_props,
                key='alpha',
                end_value=255,
                time=0.1,
                ease_type=tweencurves.easeOutCirc,
                delay=delay
            ))

            delay += 0.75
            self.tween_list.append(tween.to(
                container=self.game_logo_props,
                key='scale',
                end_value=1,
                time=0.75,
                ease_type=tweencurves.easeOutElastic,
                delay=delay
            ))
            self.tween_list.append(tween.to(
                container=self.game_logo_props,
                key='alpha',
                end_value=255,
                time=0.1,
                ease_type=tweencurves.easeOutCirc,
                delay=delay
            )) 

            delay += 0.75
            self.tween_list.append(tween.to(
                container=self.question_text_props,
                key='scale',
                end_value=1,
                time=0.75,
                ease_type=tweencurves.easeOutCirc,
                delay=delay
            ))
            self.tween_list.append(tween.to(
                container=self.question_text_props,
                key='alpha',
                end_value=255,
                time=0.1,
                ease_type=tweencurves.easeOutCirc,
                delay=delay
            ))

            self.tween_list.append(tween.to(
                container=self.no_button_props,
                key='scale',
                end_value=1,
                time=0.75,
                ease_type=tweencurves.easeOutCirc,
                delay=delay
            ))
            self.tween_list.append(tween.to(
                container=self.no_button_props,
                key='alpha',
                end_value=255,
                time=0.1,
                ease_type=tweencurves.easeOutCirc,
                delay=delay
            ))
            def finished_tween():
                self.finished_tween = True
            self.tween_list.append(tween.to(
                container=self.yes_button_props,
                key='scale',
                end_value=1,
                time=0.75,
                ease_type=tweencurves.easeOutCirc,
                delay=delay
            ).on_complete(finished_tween))
            self.tween_list.append(tween.to(
                container=self.yes_button_props,
                key='alpha',
                end_value=255,
                time=0.1,
                ease_type=tweencurves.easeOutCirc,
                delay=delay
            ))

        else:
            self.game.start_menu_music()
            self.finished_tween = True
            self.finish_bootup_skip()


    def finish_bootup(self):
        self.game.finished_bootup = True

        # Clear intro assets
        del self.surface_logo
        del self.surface_logo_props
        del self.overlay
        del self.overlay_props

        # Clear tween list
        self.tween_list.clear()

        # Set props to final values
        for layer in self.landscape_list:
            layer['y_offset'] = 0
        self.winds_props['y_offset'] = 0
        self.game_logo_props['scale'] = 1
        self.game_logo_props['alpha'] = 255

        # Convert surfaces to static
        self.game_logo = pygame.transform.scale_by(surface=self.game_logo, factor=self.game_logo_props['scale'])
        
        # Initiate substate
        # Menu_TitleState(game=self.game, parent=self, stack=self.substate_stack).enter_state()

    def finish_bootup_skip(self):
        """Called when skipping bootup animation - sets all elements to visible"""
        self.game.finished_bootup = True

        # Clear intro assets
        del self.surface_logo
        del self.surface_logo_props
        del self.overlay
        del self.overlay_props

        # Clear tween list
        self.tween_list.clear()

        # Set props to final values
        for layer in self.landscape_list:
            layer['y_offset'] = 0
        self.winds_props['y_offset'] = 0
        
        # Set text elements to visible when skipping
        self.welcome_text_props['scale'] = 1
        self.welcome_text_props['alpha'] = 255
        self.game_logo_props['scale'] = 1
        self.game_logo_props['alpha'] = 255
        self.question_text_props['scale'] = 1
        self.question_text_props['alpha'] = 255
        self.no_button_props['scale'] = 1
        self.no_button_props['alpha'] = 255
        self.yes_button_props['scale'] = 1
        self.yes_button_props['alpha'] = 255

        # Convert surfaces to static
        self.game_logo = pygame.transform.scale_by(surface=self.game_logo, factor=self.game_logo_props['scale'])
