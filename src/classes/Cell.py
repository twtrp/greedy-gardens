class Cell():
    def __init__(self, index):
        self.position = index
        self.path_type = None
        self.fruit = [("strawberry", 0), ("orange",0 ),("blueberry",0),("kiwi",0),("coconut",0),("peach",0)]
        self.home=False
        self.magic_fruit=0
        # for direction
        self.north=False
        self.west=False
        self.east=False
        self.south=False
        # for checking logic
        self.path=False
        self.temp=False

    def set_path(self, path_type):
        if self.path_type is None:
            self.path_type = path_type
        else:
            pass

    def add_fruit(self, fruit_type, value):
        for i in range(len(self.fruit)):
            if self.fruit[i][0] == fruit_type:
                self.fruit[i] = (self.fruit[i][0], self.fruit[i][1] + value)
                break
            
    def show_detail(self):
        print(self.path_type)
        print(self.fruit)
        print(self.home)
        print(self.magic_fruit)
        print(f"N: {self.north}, W: {self.west}, E: {self.east}, S: {self.south}")

    def would_be_same(self, other_cell):
        directions = ['north', 'west', 'east', 'south']
        
        for direction in directions:
            current_value = getattr(self, direction)
            combined_value = current_value or getattr(other_cell, direction)
            
            if combined_value != current_value:
                return False
        
        return True
    
    def is_the_same(self, other_cell):
        directions = ['north', 'west', 'east', 'south']
        
        for direction in directions:
            current_value = getattr(self, direction)
            another_value = getattr(other_cell, direction)
            
            if another_value != current_value:
                return False
        
        return True
    
    def combine_directions(self, other_cell):
        directions = ['north', 'west', 'east', 'south']
        
        for direction in directions:
            setattr(self, direction, getattr(self, direction) or getattr(other_cell, direction))

    def swap_path(cell1, cell2):
        cell1.north, cell2.north = cell2.north, cell1.north
        cell1.south, cell2.south = cell2.south, cell1.south
        cell1.east, cell2.east = cell2.east, cell1.east
        cell1.west, cell2.west = cell2.west, cell1.west
        
        cell1.temp, cell2.temp = cell2.temp, cell1.temp