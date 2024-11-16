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
        self.board[index].north = True
        self.board[index].west = True
        self.board[index].east = True
        self.board[index].south = True
    
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
        # This list keep index of house and magic fruits. Used in fruits generation logic
        unique_index = []

        # Set home location
        home_index = random.randint(1, 6) * 8 + random.randint(1, 6) # index = row*8 + column with home not at the edge
        home_quadrant = self.check_quadrant(home_index)
        self.set_home(home_index)

        unique_index.append(home_index)

        # Set Magic Fruits Location
        no_mfruit_index = self.diamond_radius(home_index)
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
                        unique_index.append(mfruitindex)
                        loop = False
            elif current_quadrant == 2:
                while loop: 
                    # index = row * 8 + column
                    mfruitindex = random.randint(1, 3) * 8 + random.randint(1, 3)
                    if mfruitindex not in no_mfruit_index:
                        self.set_magic_fruit(mfruitindex, mfruitnum)
                        unique_index.append(mfruitindex)
                        loop = False
            elif current_quadrant == 3:
                while loop: 
                    # index = row * 8 + column
                    mfruitindex = random.randint(4, 6) * 8 + random.randint(1, 3)
                    if mfruitindex not in no_mfruit_index:
                        self.set_magic_fruit(mfruitindex, mfruitnum)
                        unique_index.append(mfruitindex)
                        loop = False
            elif current_quadrant == 4:
                while loop: 
                    # index = row * 8 + column
                    mfruitindex = random.randint(4, 6) * 8 + random.randint(4, 6)
                    if mfruitindex not in no_mfruit_index:
                        self.set_magic_fruit(mfruitindex, mfruitnum)
                        unique_index.append(mfruitindex)
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
        all_fruit = ["fruit_strawberry", "fruit_orange", "fruit_blueberry", "fruit_grape", "fruit_coconut", "fruit_peach"]

        # debug
        # loopnumber = 0
        # test_fruit = ["fruit_strawberry"]

        for fruit in all_fruit:
            placed = 0
            while placed < fruit_each_type:
                # print(loopnumber)
                fruit_quadrant = random.choice(available_quadrant)
                quadrant_index = fruit_quadrant - 1
                if fruit_quadrant == 1:
                    fruit_index = random.randint(0, 3) * 8 + random.randint(4, 7)
                elif fruit_quadrant == 2:
                    fruit_index = random.randint(0, 3) * 8 + random.randint(0, 3)
                elif fruit_quadrant == 3:
                    fruit_index = random.randint(4, 7) * 8 + random.randint(0, 3)
                elif fruit_quadrant == 4:
                    fruit_index = random.randint(4, 7) * 8 + random.randint(4, 7)
                
                '''
                Fruits generation has 4 conditions
                1. The number of fruit in that quadrant must not exceed max_fruit_each_quadrant.
                2. The number of fruit in a cell must not exceed max_fruit_cell.
                3. In that cell, there must be no more than max_type_cell instances of the same fruit type.
                4. The index of the fruit must not be that of home and magic fruits.
                Note: There are 6 types of fruits, each has fruit_each_type instances.
                '''
                fruit_cond1 = board_fruit[quadrant_index] < max_fruit_each_quadrant
                fruit_cond2 = self.board[fruit_index].sum_fruit() < max_fruit_cell
                fruit_cond3 = self.board[fruit_index].valid_fruit_cell(max_type_cell)
                fruit_cond4 = fruit_index not in unique_index

                if fruit_cond1 and fruit_cond2 and fruit_cond3 and fruit_cond4:
                    self.add_fruit(fruit_index, fruit)
                    placed += 1
                    # print(f"Placed {fruit} at index {fruit_index}. Total placed: {placed}")
                    board_fruit[quadrant_index] += 1
                    if board_fruit[quadrant_index] == max_fruit_each_quadrant:
                        available_quadrant.remove(fruit_quadrant)
                
                # loopnumber+=1
    
    '''
    Check Connected Path
    - Recursively checking West -> North -> East -> South for the connection
    - Have additional condition to check if the index is already included in the connected path to prevent infinite cycle
    '''

    def check_connection(self, connected_indices, center_index):
        connected_indices.append(center_index)
        west_index = center_index - 1
        north_index = center_index - 8
        east_index = center_index + 1
        south_index = center_index + 8
        if 0 <= west_index <= 63:
            if self.board[west_index].east and west_index not in connected_indices:
                self.check_connection(connected_indices, west_index)
        if 0 <= north_index <= 63:
            if self.board[north_index].south and north_index not in connected_indices:
                self.check_connection(connected_indices, north_index)
        if 0 <= east_index <= 63:
            if self.board[east_index].west and east_index not in connected_indices:
                self.check_connection(connected_indices, east_index)
        if 0 <= south_index <= 63:
            if self.board[south_index].north and south_index not in connected_indices:
                self.check_connection(connected_indices, south_index)
        

    def board_eval(self, home_index, today_fruit):
        connected_indices = self.check_connection(home_index)
        score = 0
        for i in connected_indices:
            cell_fruit = self.board[i].fruit
            if cell_fruit:
                for fruit in cell_fruit:
                    # Will change this condition later after asking Three how the fruit name is passed
                    if fruit in today_fruit or today_fruit in fruit or fruit == today_fruit:
                        score += 1
        return score

        
                
