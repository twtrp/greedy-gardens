from abc import ABC, abstractmethod

class BaseEntity(ABC):
    def __init__(self):
        self.active = True
        self.x = 0
        self.y = 0


    @abstractmethod
    def update(self, dt, events):
        pass


    @abstractmethod
    def render(self):
        pass
    