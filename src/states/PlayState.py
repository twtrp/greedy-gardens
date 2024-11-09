from src.library.essentials import *
from src.template.BaseState import BaseState
from src.states.Play_StartState import Play_StartState
import tween

class PlayState(BaseState):
    def __init__(self, game, parent, stack, seed):
        BaseState.__init__(self, game, parent, stack, seed)

        print("Entered PlayState")
        self.game.canvas.fill((0, 0, 0))
        print(seed)

        self.substate_stack = []

        self.ready = False
        self.load_assets()
        self.ready = True

        self.finished_boot_up = False
        
        # utils.music_load(music_channel=self.game.music_channel, name='menu_intro.ogg')
        # utils.music_queue(music_channel=self.game.music_channel, name='menu_loop.ogg', loops=-1)
        # self.game.music_channel.play()

        # self.tween_list = []
        # if not self.finished_boot_up:
        #     self.bootup_tween_chain(skip=self.game.settings['skip_bootup'])
        # else:
        #     self.bootup_tween_chain(skip=True)

    #Main methods

    def load_assets(self):
        # Load white overlay
        self.overlay = pygame.Surface(size=(constants.canvas_width, constants.canvas_height), flags=pygame.SRCALPHA)
        self.overlay_props = {'alpha': 255}
        self.overlay.fill(color=(*colors.white, self.overlay_props['alpha']))
        
        # # Load intro assets
        # self.logo = utils.get_image(dir=dir.graphics, name='namsom_logo.png', mode='colorkey')
        # self.logo = pygame.transform.scale_by(surface=self.logo, factor=7)
        # self.surface_logo = pygame.Surface(size=(self.logo.get_width(), self.logo.get_height()+50), flags=pygame.SRCALPHA)
        # self.surface_logo_props = {'y_offset': 0, 'alpha': 0, 'scale': 0.7}
        # utils.blit(dest=self.surface_logo, source=self.logo)
        # text = utils.get_text(text='PRESENTS', font=fonts.retro_arcade, size='small', color=colors.mono_100,
        #                       long_shadow_color=utils.color_lighten(color=colors.mono_100,factor=0.75),
        #                       outline_color=colors.white)
        # utils.blit(dest=self.surface_logo, 
        #            source=text,
        #            pos=(self.surface_logo.get_width()/2, self.surface_logo.get_height()/2 + 30),
        #            pos_anchor=posanchors.midtop)

        # Load menu background assets
        self.landscape_list = [
            {
                'image': utils.get_image(dir=dir.play_bg, name='grass_pattern.png', mode='colorkey'),
            },
            {
                'image': utils.get_image(dir=dir.play_bg, name='water_low.png', mode='colorkey'),
            },
            {
                'image': utils.get_image(dir=dir.play_bg, name='water_high.png', mode='colorkey'),
            },
            {
                'image': utils.get_image(dir=dir.play_bg, name='trees_bridges.png', mode='colorkey'),
            },
            {
                'image': utils.get_image(dir=dir.play_bg, name='fence.png', mode='colorkey'),
            },
        ]

    def update(self, dt, events):
        if self.ready:

            # Update substates
            if self.substate_stack:
                self.substate_stack[-1].update(dt=dt, events=events)

            # Update tweens
            tween.update(passed_time=dt)

        for event in events:
            # print(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # print("entering")
                    Play_StartState(game=self.game, parent=self.parent, stack=self.substate_stack).enter_state()
                if event.key == pygame.K_ESCAPE:
                        # print("exiting")
                        self.exit_state()

        utils.set_cursor(cursor=self.cursor)
        self.cursor = cursors.normal


    def render(self, canvas):
        
        if self.ready:

            # Build background

            ## Render landscape to menu_bg
            for layer in self.landscape_list:
                utils.blit(dest=canvas, source=layer['image'], pos=(0, 0))
                
            # Render substates

            if not self.substate_stack:

                # ## Render menu options
                # for i, option in enumerate(self.title_button_option_surface_list):
                #     processed_option = pygame.transform.scale_by(surface=option['surface'], factor=option['scale'])
                #     processed_option.set_alpha(option['alpha'])
                #     utils.blit(dest=canvas, source=processed_option, pos=(constants.canvas_width/2, 340 + i*80), pos_anchor=posanchors.center)

                pass

            else:
                self.substate_stack[-1].render(canvas=canvas)          
                

    #Class methods
  
    # def bootup_tween_chain(self, skip=False):
    #     if not skip:
    #         delay = 0
    #         self.tween_list.append(tween.to(container=self.surface_logo_props,
    #                                         key='alpha',
    #                                         end_value=255,
    #                                         time=2,
    #                                         ease_type=tweencurves.easeOutCubic,
    #                                         delay=delay))
    #         self.tween_list.append(tween.to(container=self.surface_logo_props,
    #                                         key='scale',
    #                                         end_value=1,
    #                                         time=3,
    #                                         ease_type=tweencurves.easeOutCubic,
    #                                         delay=delay))

    #         delay = 1.75
    #         self.tween_list.append(tween.to(container=self.overlay_props,
    #                                         key='alpha',
    #                                         end_value=0,
    #                                         time=2,
    #                                         ease_type=tweencurves.easeOutQuad,
    #                                         delay=delay))
    #         for layer in self.landscape_list:
    #             self.tween_list.append(tween.to(container=layer,
    #                                             key='y_offset',
    #                                             end_value=0,
    #                                             time=3.25,
    #                                             ease_type=tweencurves.easeOutQuint,
    #                                             delay=delay))
                
    #         self.tween_list.append(tween.to(container=self.winds_props,
    #                                         key='y_offset',
    #                                         end_value=0,
    #                                         time=3.25,
    #                                         ease_type=tweencurves.easeOutQuint,
    #                                         delay=delay))
    #         self.tween_list.append(tween.to(container=self.surface_logo_props,
    #                                         key='y_offset',
    #                                         end_value=-500,
    #                                         time=3.25,
    #                                         ease_type=tweencurves.easeOutQuint,
    #                                         delay=delay).on_complete(self.finish_bootup))
            
    #         delay = 4
    #         self.tween_list.append(tween.to(container=self.game_logo_props,
    #                                         key='scale',
    #                                         end_value=1,
    #                                         time=0.75,
    #                                         ease_type=tweencurves.easeOutElastic,
    #                                         delay=delay))
    #         self.tween_list.append(tween.to(container=self.game_logo_props,
    #                                         key='alpha',
    #                                         end_value=255,
    #                                         time=0.1,
    #                                         ease_type=tweencurves.easeOutCirc,
    #                                         delay=delay))
            
    #         for option in self.title_button_option_surface_list:
    #             delay += 0.125
    #             self.tween_list.append(tween.to(container=option,
    #                                             key='scale',
    #                                             end_value=1,
    #                                             time=0.5,
    #                                             ease_type=tweencurves.easeOutElastic,
    #                                             delay=delay))
    #             self.tween_list.append(tween.to(container=option,
    #                                             key='alpha',
    #                                             end_value=255,
    #                                             time=0.1,
    #                                             ease_type=tweencurves.easeOutCirc,
    #                                             delay=delay))
                
    #     else:
    #         self.finish_bootup()


    # def finish_bootup(self):
    #     self.finished_boot_up = True

    #     # Clear intro assets
    #     del self.overlay
    #     del self.overlay_props

    #     # Set props to final values
    #     for layer in self.landscape_list:
    #         layer['y_offset'] = 0
    #         self.winds_props['y_offset'] = 0
    #         self.game_logo_props['scale'] = 1
    #         self.game_logo_props['alpha'] = 255
    #         for option in self.title_button_option_surface_list:
    #             option['scale'] = 1
    #             option['alpha'] = 255

    #     # Convert surfaces to static
    #     self.game_logo = pygame.transform.scale_by(surface=self.game_logo, factor=self.game_logo_props['scale'])
    #     for option in self.title_button_option_surface_list:
    #         option['surface'] = pygame.transform.scale_by(surface=option['surface'], factor=option['scale'])
        
    #     # Initiate substate
    #     Play_StartState(game=self.game, parent=self, stack=self.substate_stack).enter_state()