from src.library.essentials import *
from src.states.TitleState import TitleState

class Game:
    def __init__(self):
        self.canvas_width, self.canvas_height = 1280, 720
        self.screen_width, self.screen_height = 1440, 810
        self.max_fps = 30
        self.max_fps += 1
        self.title = 'Greedy Gardens'

        self.ready = False
        self.started = False
        pygame.mixer.pre_init(44100, 16, 2, 4096)
        pygame.init()
        pygame.display.set_icon(pygame.image.load(os.path.join(utils.graphics_dir, 'icon.png')))
        pygame.display.set_caption(self.title+' (0 FPS)')
        self.canvas = pygame.Surface(size=(self.canvas_width, self.canvas_height))
        self.screen = pygame.display.set_mode(size=(self.screen_width, self.screen_height), flags=pygame.HWSURFACE|pygame.DOUBLEBUF)
        self.screen.fill(color=utils.get_mono_color(255))
        pygame.display.update()

        self.clock = pygame.time.Clock()
        self.music_channel = pygame.mixer.music
        self.music_channel.set_volume(1)
        self.ambience_channel = pygame.mixer.Channel(0)
        self.ambience_channel.set_volume(0.2)

        self.state_stack = []
        utils.sound_play(sound_channel=self.ambience_channel, sound_name='ambience.ogg', loops=-1, fade_ms=3000)


    def update(self, dt, events):
        if self.ready: 
            if self.state_stack:
                self.state_stack[-1].update(dt=dt, events=events)
            else:
                self.state_stack.append(TitleState(game=self))
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.mixer.stop()
                    pygame.quit()
                    sys.exit()
    

    def render(self):
        self.canvas.fill(color=utils.get_mono_color(255))
        if self.state_stack:
            self.state_stack[-1].render(surface=self.canvas)
        scaled_canvas = pygame.transform.scale(surface=self.canvas, size=(self.screen_width, self.screen_height))
        utils.blit(dest=self.screen, source=scaled_canvas)
        pygame.display.update()

        if not self.ready:
            self.ready = True


    def game_loop(self):
        while True:
            pygame.display.set_caption(f'{self.title} ({int(self.clock.get_fps())} FPS)')
            dt = self.clock.tick(self.max_fps)/1000.0
            events = pygame.event.get()
            if self.ready:
                self.update(dt=dt, events=events)
            self.render()


if __name__ == '__main__':
    game = Game()
    game.game_loop()
