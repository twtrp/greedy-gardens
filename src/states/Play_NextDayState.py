from src.library.essentials import *
from src.template.BaseState import BaseState

class Play_NextDayState(BaseState):
    def __init__(self, game, parent, stack):
        BaseState.__init__(self, game, parent, stack)
        self.parent = parent

        print("Next Day")

    def update(self, dt, events):
        self.parent.strikes = 0
        self.parent.current_day += 1

        self.exit_state()

    def render(self, canvas):
        pass
        # Should have text showing Days number