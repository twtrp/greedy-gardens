from src.library.essentials import *
from src.states.MenuState import MenuState

class Game:
    def __init__(self):
        self.max_fps = constants.max_fps + 1
        self.title = 'Greedy Gardens'

        pygame.mixer.pre_init(frequency=44100, size=16, channels=2, buffer=4096)
        pygame.init()
        pygame.display.set_icon(pygame.image.load(os.path.join(dir.graphics, 'icon.png')))
        pygame.display.set_caption(self.title+' (0 FPS)')
        self.canvas = pygame.Surface(size=(constants.canvas_width, constants.canvas_height))
        self.screen = pygame.display.set_mode(size=(constants.screen_width, constants.screen_height), flags=pygame.HWSURFACE|pygame.DOUBLEBUF)
        self.screen.fill(color=colors.white)
        pygame.display.update()
        self.clock = pygame.time.Clock()

        self.music_channel = pygame.mixer.music
        self.music_channel.set_volume(constants.music_volume)
        self.ambience_channel = pygame.mixer.Channel(0)
        self.ambience_channel.set_volume(constants.ambience_volume)
        utils.sound_play(sound_channel=self.ambience_channel, sound_name='ambience.ogg', loops=-1, fade_ms=3000)
        utils.set_cursor(image=utils.load_sprite(sprite_sheet=spritesheets.cursors, target_sprite='cursor_normal'))

        self.state_stack = []


    def update(self, dt, events):
        # Update current state
        if self.state_stack:
            self.state_stack[-1].update(dt=dt, events=events)
        else:
            MenuState(parent=self, stack=self.state_stack).enter_state()
            pass

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
        if (constants.canvas_width, constants.canvas_height) != (constants.screen_width, constants.screen_height):
            scaled_canvas = pygame.transform.scale(surface=self.canvas, size=(constants.screen_width, constants.screen_height))
            utils.blit(dest=self.screen, source=scaled_canvas)
        else:
            utils.blit(dest=self.screen, source=self.canvas)
            
        # Update display
        pygame.display.update()


    def game_loop(self):
        while True:
            pygame.display.set_caption(f'{self.title} ({int(self.clock.get_fps())} FPS)')
            dt = self.clock.tick(self.max_fps)/1000.0
            events = pygame.event.get()
            self.update(dt=dt, events=events)
            self.render()


if __name__ == '__main__':
    game = Game()
    game.game_loop()
