from src.library.essentials import *

class TimerManager(object):
    
    def StartTimer(self, timer, transition_time_ms):
        pygame.time.set_timer(timer, transition_time_ms)

    def StopTimer(self, timer):
        pygame.time.set_timer(timer, 0)
