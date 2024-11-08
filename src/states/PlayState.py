from src.library.essentials import *
from src.template.BaseState import BaseState
from src.states.Play_StartState import Play_StartState
import tween

class PlayState(BaseState):
    def __init__(self, game, parent, stack):
        BaseState.__init__(self, game, parent, stack)

        print("Entered PlayState")
        self.game.canvas.fill((0, 0, 0))

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
        
        # Load background
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
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    print("entering")
                    Play_StartState(game=self.game, parent=self.parent, stack=self.substate_stack).enter_state()
                if event.key == pygame.K_ESCAPE:
                        print("exiting")
                        self.exit_state()


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
                #     utils.blit(dest=canvas, source=processed_option, pos=(constants.canvas_width/2, 340 + i*80), pos_anchor='center')

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