#Class of square
class Square:
    #Init method to save square values
    def __init__(self,color,piece = None):
        self.color = color
        self.piece = piece
    #Method to assign a piece to the square
    def assign_piece(self,piece):
        self.piece = piece
    #Method to deallocate the piece of the square
    def deallocate_piece(self):
        self.piece =  None
    #Method to return if is a piece inside the square
    def is_piece_inside(self):
        return self.piece != None
    #Method to return the color of the piece inside
    def piece_color(self):
        return self.piece.get_piece_color()
    #Method to return the piece inside the square
    def get_piece(self):
        return self.piece #xd