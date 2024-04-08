#Class of players
class Player:
    pieces = []
    #Init method to save player values
    def __init__(self,name,p_color,num):
        self.name = name
        self.p_color = p_color
        self.num = num
        self.pieces = []
    #Method to return the player name
    def get_name_player(self):
        return self.name
    #Method to add pieces to the player
    def add_piece(self,piece):
        self.pieces.append(piece)
    #Method to remove player pieces
    def remove_piece(self,piece):
        if piece in self.pieces:
            self.pieces.remove(piece)
    #Method to count quantity of pieces
    def get_amount_pieces(self):
        return len(self.pieces)
    #Method to return all player pieces
    def get_list_pieces(self):
        return self.pieces
    #Method to return the last piece added
    def get_last_piece(self):
        return self.pieces[-1]
    #Method to return player color
    def get_player_color(self):
        return self.p_color
    #Method to return player number
    def get_player_num(self):
        return self.num
    #Method to return the direction of the player's pieces
    def get_player_dir(self):
        return +1 if self.num == 2 else -1