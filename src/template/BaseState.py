from abc import ABC, abstractmethod
from src.library.essentials import *

class BaseState(ABC):
    def __init__(self, game, parent, stack, *args):
        self.game = game
        self.parent = parent
        self.stack = stack
        self.prev_state = None
        self.cursor = cursors.normal
        self.params = args


    @abstractmethod
    def update(self, dt, events):
        pass

    
    @abstractmethod
    def render(self, surface):
        pass

    
    def enter_state(self):
        if len(self.stack) > 1:
            self.prev_state = self.stack[-1]
        self.stack.append(self)


    def exit_state(self):
        self.stack.pop()
        