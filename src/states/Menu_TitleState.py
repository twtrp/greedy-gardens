from src.library.essentials import *
from src.template.BaseState import BaseState
from src.states.Menu_PlayState import Menu_PlayState

class Menu_TitleState(BaseState):
    def __init__(self, parent, stack):
        BaseState.__init__(self, parent, stack)

    #Main methods

    def update(self, dt, events):
        mouse_pos = pygame.mouse.get_pos()
        for event in events:
            for i, option in enumerate(self.parent.title_options_surfaces):
                if option['rect'].collidepoint(mouse_pos):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if i == 0:
                            Menu_PlayState(parent=self.parent, stack=self.stack).enter_state()
                        elif i == 1:
                            pass
                        elif i == 2:
                            pass
                        elif i == 3:
                            pygame.mixer.stop()
                            pygame.quit()
                            sys.exit()

    def render(self, canvas):
        # Render game logo
        utils.blit(dest=canvas, source=self.parent.game_logo, pos=(self.parent.parent.canvas_width/2, 150), pos_anchor='center')
        # Render menu options
        for i, option in enumerate(self.parent.title_options_surfaces):
            utils.blit(dest=canvas, source=option['surface'], pos=option['rect'].center, pos_anchor='center')
