from src.classes.Cell import Cell

class GameBoard():
    def __init__(self):
        self.board = []
        
        for i in range(64):
            self.board.append(Cell(i))
    
    def set_path(self,index, path_type):
        self.board[index].set_path(path_type)
    
    def add_fruit(self,index, fruit_type, value):
        self.board[index].add_fruit(fruit_type, value)
        
    def set_home(self, index):
        self.board[index].set_path("home")
        self.board[index].home = True
    
    def set_magic_fruit(self,index,num):
        self.board[index].magic_fruit=num
