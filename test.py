from src.library.essentials import *
from src.states.MenuState import MenuState
from src.components.Button import Button

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
        self.text = utils.get_text(text='Hello World', font=fonts.lf2, size='medium', color=colors.white)
        self.button = Button(id='test', surface=self.text, pos=(constants.canvas_width/2, constants.canvas_height/2), pos_anchor='center', padding_x=10, padding_y=10)

    def update(self, dt, events):
        self.button.update(dt=dt, events=events)

        if self.button.hovered:
            print('Hovered')

        if self.button.clicked:
            print('=======')
            print('Clicked')
            print('=======')

        # Handle quit
        for event in events:
            if event.type == pygame.QUIT:
                pygame.mixer.stop()
                pygame.quit()
                sys.exit()
    

    def render(self):
        # Render canvas to screen
        if (constants.canvas_width, constants.canvas_height) != (constants.screen_width, constants.screen_height):
            scaled_canvas = pygame.transform.scale(surface=self.canvas, size=(constants.screen_width, constants.screen_height))
            utils.blit(dest=self.screen, source=scaled_canvas)
        else:
            utils.blit(dest=self.screen, source=self.canvas)
        utils.blit(dest=self.canvas, source=self.text, pos=(constants.canvas_width/2, constants.canvas_height/2), pos_anchor='center')
        self.button.render(self.canvas)
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
