from src.library.essentials import *
from src.classes.SettingsManager import SettingsManager
from src.states.MenuState import MenuState

class Game:
    def __init__(self):
        self.settings_manager = SettingsManager()
        self.settings = self.settings_manager.load_all_settings()
        self.fps_cap = self.settings['fps_cap'] + 1

        self.version_number = 'v2.0.0-beta3'
        self.title = f'Greedy Gardens {self.version_number}'

        pygame.mixer.pre_init(frequency=44100, size=16, channels=2, buffer=4096)
        pygame.init()
        pygame.display.set_icon(pygame.image.load(os.path.join(dir.graphics, 'icon.png')))
        pygame.display.set_caption(self.title)
        self.canvas = pygame.Surface(size=(constants.canvas_width, constants.canvas_height))
        self.display_info = pygame.display.Info()
        
        if self.settings['fullscreen']:
            self.screen_width = self.display_info.current_w
            self.screen_height = self.display_info.current_h
            self.screen = pygame.display.set_mode(size=(self.screen_width, self.screen_height),
                                                  flags=pygame.FULLSCREEN|pygame.HWSURFACE|pygame.DOUBLEBUF)
        else:
            self.screen_width = constants.window_width
            self.screen_height = constants.window_height
            self.screen = pygame.display.set_mode(size=(self.screen_width, self.screen_height),
                                                  flags=pygame.HWSURFACE|pygame.DOUBLEBUF)

        utils.set_cursor(cursor=cursors.normal)
        self.screen.fill(color=colors.white)
        pygame.display.update()
        self.clock = pygame.time.Clock()

        self.music_channel = pygame.mixer.music
        self.music_channel.set_volume(self.settings['music_volume'])
        self.sfx_volume = self.settings['sfx_volume']
        self.ambience_channel = pygame.mixer.Channel(0)
        self.ambience_channel.set_volume(self.settings['ambience_volume'] * 0.75)
        utils.sound_play(sound=sfx.ambience, sound_channel=self.ambience_channel, loops=-1, fade_ms=3000)

        self.state_stack = []
        utils.music_load(music_channel=self.music_channel, name=music.menu_loop)
        utils.music_queue(music_channel=self.music_channel, name=music.menu_loop, loops=-1)

        self.finished_bootup = False


    # Class methods

    def apply_settings(self, setting_index):
        self.settings = self.settings_manager.load_all_settings()
        if setting_index == 0:
            self.music_channel.set_volume(self.settings['music_volume']*1)
        if setting_index == 1:
            self.sfx_volume = self.settings['sfx_volume']
        if setting_index == 2:
            self.ambience_channel.set_volume(self.settings['ambience_volume']*0.75)
        if setting_index == 3:
            pygame.mouse.set_pos((self.screen_width/2, self.screen_height/2))
            
            if self.settings['fullscreen']:
                self.screen_width = self.display_info.current_w
                self.screen_height = self.display_info.current_h
                self.screen = pygame.display.set_mode(size=(self.screen_width, self.screen_height),
                                                        flags=pygame.FULLSCREEN|pygame.HWSURFACE|pygame.DOUBLEBUF)
            else:
                self.screen_width = constants.window_width
                self.screen_height = constants.window_height
                self.screen = pygame.display.set_mode(size=(self.screen_width, self.screen_height),
                                                    flags=pygame.HWSURFACE|pygame.DOUBLEBUF)
            
            pygame.display.set_icon(pygame.image.load(os.path.join(dir.graphics, 'icon.png')))
            pygame.mouse.set_pos((self.screen_width/2, self.screen_height/2))
        if setting_index == 4:
            self.fps_cap = self.settings['fps_cap'] + 1

    def start_menu_music(self):
        if not self.music_channel.get_busy():
            self.music_channel.play()


    # Main methods

    def update(self, dt, events):
        # Update current state
        if self.state_stack:
            self.state_stack[-1].update(dt=dt, events=events)
        else:
            MenuState(game=self, parent=self, stack=self.state_stack, finished_bootup=self.finished_bootup).enter_state()

        # Handle quit
        for event in events:
            if event.type == pygame.QUIT:
                pygame.mixer.stop()
                pygame.quit()
                sys.exit()
    

    def render(self):
        # Render current state
        if self.state_stack:
            self.state_stack[-1].render(canvas=self.canvas)

        # Render canvas to screen
        if (constants.canvas_width, constants.canvas_height) != (self.screen_width, self.screen_height):
            scaled_canvas = pygame.transform.scale(surface=self.canvas, size=(self.screen_width, self.screen_height))
            utils.blit(dest=self.screen, source=scaled_canvas)
        else:
            utils.blit(dest=self.screen, source=self.canvas)
        
        # Update display
        pygame.display.update()


    def game_loop(self):
        while True:
            try:
                # pygame.display.set_caption(f'{self.title} ({int(self.clock.get_fps())} FPS)')
                dt = self.clock.tick(self.fps_cap)/1000.0
                events = pygame.event.get()
                self.update(dt=dt, events=events)
                self.render()
            except KeyboardInterrupt:
                pygame.mixer.stop()
                pygame.quit()
                sys.exit()


if __name__ == '__main__':
    game = Game()
    game.game_loop()
