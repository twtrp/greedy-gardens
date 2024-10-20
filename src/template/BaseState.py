from abc import ABC, abstractmethod

class BaseState(ABC):
    def __init__(self, game):
        self.game = game
        self.prev_state = None


    @abstractmethod
    def update(self, dt, events):
        pass

    
    @abstractmethod
    def render(self, surface):
        pass

    
    def enter_state(self):
        if len(self.game.state_stack) > 1:
            self.prev_state = self.game.state_stack[-1]
        self.game.state_stack.append(self)


    def exit_state(self):
        self.game.state_stack.pop()
        