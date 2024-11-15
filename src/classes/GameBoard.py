from src.classes.Cell import Cell
import random

class GameBoard():
    def __init__(self, seed):
        self.board = []
        self.seed = seed

        random.seed(self.seed)

        for i in range(64):
            self.board.append(Cell(i))

        # Set the board (Home, Magic Fruits, and Fruits)
        self.set_board()
        
    def set_path(self,index, path_type):
        self.board[index].set_path(path_type)
    
    def add_fruit(self,index, fruit_type):
        self.board[index].add_fruit(fruit_type)
        
    def set_home(self, index):
        self.board[index].set_path("home")
        self.board[index].home = True
        self.north=True
        self.west=True
        self.east=True
        self.south=True
        self.path=True
    
    def set_magic_fruit(self,index,num):
        self.board[index].magic_fruit=num
        
    def show_detail(self, index):
        self.board[index].show_detail()

    def check_quadrant(self, index):
        # Calculate row and column
        row = index // 8
        column = index % 8

        # Determine the quadrant based on row and column
        if row < 4 and column < 4:
            return 1  # Quadrant 1
        elif row < 4 and column >= 4:
            return 2  # Quadrant 2
        elif row >= 4 and column < 4:
            return 3  # Quadrant 3
        else:
            return 4  # Quadrant 4
    
    # Create radius around home where magic fruit will not spawn, this includes the home tile
    def diamond_radius(self, index):
        home_row = index // 8
        home_col = index % 8

        diamond_indices = []

        # Home index
        diamond_indices.append(index)
        
        # Loop through potential positions in the diamond range
        for row_offset in range(-2, 3):   # Rows from -2 to +2 around home_row
            for col_offset in range(-2, 3):  # Columns from -2 to +2 around home_col
                # Calculate new position
                new_row = home_row + row_offset
                new_col = home_col + col_offset
                
                # Check if within bounds of the 8x8 grid
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    # Check if the Manhattan distance is exactly 2 (Diamond Shape) or 1 (Directly adjacent)
                    if abs(row_offset) + abs(col_offset) == 2 or abs(row_offset) + abs(col_offset) == 1:
                        # Convert coordinate back to index (row*8 + col)
                        diamond_indices.append(new_row * 8 + new_col)
        
        return diamond_indices
    
    def set_board(self):
        # Set home location
        home_index = random.randint(1, 6) * 8 + random.randint(1, 6) # index = row*8 + column with home not at the edge
        home_quadrant = self.check_quadrant(home_index)
        self.set_home(home_index)

        no_mfruit_index = self.diamond_radius(home_index)

        # Set Magic Fruits Location
        mfruitquadrant = [1, 2, 3, 4]
        mfruitquadrant.remove(home_quadrant) # Possible location of magic fruit by quadrant
        for mfruitnum in range(1, 4):
            current_quadrant = mfruitquadrant.pop(0)
            loop = True
            if current_quadrant == 1:
                while loop: 
                    # index = row * 8 + column
                    mfruitindex = random.randint(1, 3) * 8 + random.randint(4, 6)
                    if mfruitindex not in no_mfruit_index:
                        self.set_magic_fruit(mfruitindex, mfruitnum)
                        loop = False
            elif current_quadrant == 2:
                while loop: 
                    # index = row * 8 + column
                    mfruitindex = random.randint(1, 3) * 8 + random.randint(1, 3)
                    if mfruitindex not in no_mfruit_index:
                        self.set_magic_fruit(mfruitindex, mfruitnum)
                        loop = False
            elif current_quadrant == 3:
                while loop: 
                    # index = row * 8 + column
                    mfruitindex = random.randint(4, 6) * 8 + random.randint(1, 3)
                    if mfruitindex not in no_mfruit_index:
                        self.set_magic_fruit(mfruitindex, mfruitnum)
                        loop = False
            elif current_quadrant == 4:
                while loop: 
                    # index = row * 8 + column
                    mfruitindex = random.randint(4, 6) * 8 + random.randint(4, 6)
                    if mfruitindex not in no_mfruit_index:
                        self.set_magic_fruit(mfruitindex, mfruitnum)
                        loop = False

        # Set fruit location
        # current fruit number in each quadrant
        board_fruit = [0, 0, 0, 0]

        # available quadrant for fruit placement
        available_quadrant = [1, 2, 3, 4]

        # max number of fruit per cell
        max_fruit_cell = 3

        # max fruit per type per cell
        max_type_cell = 2

        # number of fruit for each type
        fruit_each_type = 16

        # max number of fruit per quadrant
        max_fruit_each_quadrant = (fruit_each_type * 6) / 4

        # all fruit types
        all_fruit = ["strawberry", "orange", "blueberry", "kiwi", "coconut", "peach"]

        for fruit in all_fruit:
            placed = 0
            while placed < fruit_each_type:
                fruit_quadrant = random.choice(available_quadrant)
                quadrant_index = fruit_quadrant - 1
                if fruit_quadrant == 1:
                    fruit_index = random.randint(0, 3) * 8 + random.randint(4, 7)
                elif fruit_quadrant == 2:
                    fruit_index = random.randint(0, 3) * 8 + random.randint(0, 3)
                elif current_quadrant == 3:
                    fruit_index = random.randint(4, 7) * 8 + random.randint(0, 3)
                elif current_quadrant == 4:
                    fruit_index = random.randint(4, 7) * 8 + random.randint(4, 7)
                
                if ((board_fruit[quadrant_index] < max_fruit_each_quadrant) and 
                    (self.board[fruit_index].sum_fruit() < max_fruit_cell) and
                    (self.board[fruit_index].valid_fruit_cell(max_type_cell))):
                    self.add_fruit(fruit_index, fruit)
                    placed += 1
                    board_fruit[quadrant_index] += 1
                    if board_fruit[quadrant_index] == max_fruit_each_quadrant:
                        available_quadrant.remove(fruit_quadrant)
                
