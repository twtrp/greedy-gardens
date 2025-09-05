from src.library.essentials import *

class Game:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(size=(1600, 900), flags=pygame.HWSURFACE|pygame.DOUBLEBUF)
        self.fullscreen = False
        self.icon = pygame.Surface((32, 32))
        self.icon.fill("red")
        pygame.display.set_icon(self.icon)   

    def update(self, dt, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.fullscreen = not self.fullscreen
                    pygame.display.quit()
                    pygame.display.init()
                    pygame.display.set_icon(self.icon)  
                    if self.fullscreen:
                        self.screen = pygame.display.set_mode(flags=pygame.FULLSCREEN|pygame.HWSURFACE|pygame.DOUBLEBUF)
                    else:
                        self.screen = pygame.display.set_mode(size=(1600, 900), flags=pygame.HWSURFACE|pygame.DOUBLEBUF)

    def render(self):
        self.screen.fill(color=(255,255,255))
        pygame.display.update()

    def game_loop(self):
        while True:
            try:
                dt = self.clock.tick(60)/1000.0
                events = pygame.event.get()
                self.update(dt=dt, events=events)
                self.render()
            except KeyboardInterrupt:
                pygame.quit()
                sys.exit()

if __name__ == '__main__':
    game = Game()
    game.game_loop()