#Class of piece
class Piece:
    #Set the character of normal pieces
    character = "©"
    #Init method to save piece values
    def __init__(self,p_color):
        self.p_color = p_color
        self.is_queen = False
    #Method to return piece color    
    def get_piece_color(self):
        return self.p_color
    #Method to return piece character
    def get_character(self):
        return self.character
    #Method to become piece a queen
    def convert_to_queen(self):
        self.character = "♛"
        self.is_queen = True
    #Method to return is_queen
    def pieces_is_queen(self):
        return self.is_queen