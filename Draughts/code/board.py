import colorama
from colorama import Fore, Back, Style
from player import Player
from piece import Piece
from square import Square
import os
#Class of board
class Board:

    clear_text = ""
    #Init method to save board values
    def __init__(self,size_m = 8):
        self.matrix = []
        self.size_m = size_m

    #Method to generate the squares inside the board according to the size of the board and with the pieces where they correspond
    def generate_squares(self,player1,player2):

        #Variable for roaming between white and red squares
        i = True
        for y in range(0,self.size_m):
            aux = []
            x = 0
            while x < self.size_m:

                #If sentence to leave 2 rows of empty squares
                if y < (self.size_m/2) -1 or y >= (self.size_m/2) + 1:                        
                    if i:
                        aux.append(Square(Fore.WHITE))
                        i = False
                    else:

                        #If sentence to choose which player will own the piece
                        if y > self.size_m/2:
                            player1.add_piece(Piece(player1.get_player_color()))
                            aux.append(Square(Fore.RED,player1.get_last_piece()))
                        else:
                            player2.add_piece(Piece(player2.get_player_color()))
                            aux.append(Square(Fore.RED,player2.get_last_piece()))
                        i = True
                else:
                    if i:
                        aux.append(Square(Fore.WHITE))
                        i = False
                    else:
                        aux.append(Square(Fore.RED))   
                        i = True
                x += 1

            #If sentence to begin every row with a different color of square
            if i:
                i = False
            else:
                i = True
            self.matrix.append(aux)

    #Method to draw the board
    def draw_matrix(self):
        clear = lambda: os.system(self.clear_text)
        clear()
        draw_b = 'x→ '
        reset = Style.RESET_ALL
        con = 0
        for a in range(1,self.size_m+1):
            draw_b += str(a) + ' '
        draw_b += ' y↓'
        draw_b += '\n'
        for row in self.matrix:
            draw_b += '   '
            for col in row:
                if col.is_piece_inside():
                    piece_string = col.get_piece().get_character() +' '
                    draw_b += col.piece_color() + piece_string+ reset
                else:
                    draw_b += col.color + '■ '+ reset
            con += 1
            draw_b += '|'+str(con) +'\n'
        print(draw_b)

    #Method to move a piece in the board
    def move_piece(self,coordinates,playing,opponent):

        #Dictionary that establish difference of squares and the direction that the piece is trying to move
        dif_dir = self.difference_between_and_direction(coordinates)
        
        #If to verify that the movement being attempted is correct
        if not self.verify_moves(coordinates,playing,dif_dir):
            return self.wrong(playing)
        
        #If sentence to verify if the piece tries to move two squares which means that it tries to eat
        if dif_dir['dif_x'] == 2:
        
            #If sentence to verify if the piece can eat
            if not self.piece_can_eat(coordinates,playing,dif_dir):
                return self.wrong(playing)
        
            #If the piece can eat it proceeds to make the move and eliminate the attacked piece of the opponent and the board
            opponent.remove_piece(self.matrix[coordinates['to_y'] - dif_dir['dir_y']][coordinates['to_x'] - dif_dir['dir_x']].get_piece())
            self.matrix[coordinates['to_y'] - dif_dir['dir_y']][coordinates['to_x'] - dif_dir['dir_x']].deallocate_piece()
            self.matrix[coordinates['to_y']][coordinates['to_x']].assign_piece(self.matrix[coordinates['from_y']][coordinates['from_x']].get_piece())
            self.matrix[coordinates['from_y']][coordinates['from_x']].deallocate_piece()
        
            #If sentence to continue eating if the piece moved can do it
            if self.piece_can_eat_after_eat(coordinates['to_x'],coordinates['to_y'],playing) != []:
                self.draw_matrix()
                return playing
        
        #if the difference of square is one perform the movement
        else:
            self.matrix[coordinates['to_y']][coordinates['to_x']].assign_piece(self.matrix[coordinates['from_y']][coordinates['from_x']].get_piece())
            self.matrix[coordinates['from_y']][coordinates['from_x']].deallocate_piece()
        
        
        #If becomes queen is equal to true, become piece in a queen
        if self.become_queen(playing,coordinates):
            self.matrix[coordinates['to_y']][coordinates['to_x']].get_piece().convert_to_queen()
        
        #Draw matrix and return opponent to change the turn
        self.draw_matrix()
        return opponent        
    
    #Method to return if something is wrong about the move
    def wrong(self,pt,message = 'Wrong coordinates'):
        self.draw_matrix()
        print(message)
        return pt
    
    #Method that returns false if the movement cannot be performed
    def verify_moves(self,coordinates,playing,dif_dir):
        #Verify that the piece is moving diagonally and that the strings are in range
        if self.is_not_diagonal(dif_dir):
            return False
        #Verify the coordinates are in range
        if not self.coordinates_is_in_range(coordinates):
            return False
        #Verify there is a piece in the coordinate that was specified
        if not self.matrix[coordinates['from_y']][coordinates['from_x']].is_piece_inside():
            return False
        #Verify that the piece belongs to the player who is playing
        if not self.is_in_player_list(coordinates,playing):
            return False
        #Verify that there is no piece in the square that is moving
        if self.matrix[coordinates['to_y']][coordinates['to_x']].is_piece_inside():
            return False
        #Verify that the piece is not moving more than two squares and equal amount in both x and y
        if dif_dir['dif_x'] > 2 or dif_dir['dif_y'] > 2 or dif_dir['dif_x'] != dif_dir['dif_y']:
            return False
        #Verify that the pieces that are not queens cannot move backwards
        if not self.matrix[coordinates['from_y']][coordinates['from_x']].get_piece().pieces_is_queen():
            if dif_dir['dir_y'] != playing.get_player_dir():
                return False
        return True
    
    #Method to verify if the piece is in player list
    def is_in_player_list(self,coordinates,playing):
        return self.matrix[coordinates['from_y']][coordinates['from_x']].get_piece() in playing.get_list_pieces()

    #Method to verify that it is a diagonal movement
    def is_not_diagonal(self,dif_dir):
        return dif_dir['dif_x'] == 0 or dif_dir['dif_y'] == 0

    #Method to verify which forced movements are in this turn
    def verify_forced_movements(self,playing):
        
        #Array that stores the mandatory movements of the current turn
        forced = []
        #Choose the direction of the possible moves for normal pieces
        change_y = 2 if playing.get_player_dir() == 1 else -2
        index_row = 0
        #While nested to traverse the board
        while index_row < self.size_m:
            index_col = 0
            while index_col < len(self.matrix[index_row]):
                #Add the list of forced move
                test_coordinates = {
                    'index_col': index_col,
                    'index_row': index_row,
                    'change_y': change_y
                }
                forced = self.add_forced_movements(test_coordinates,playing,forced)
                #if the piece in the square is a queen piece add the list of forced move in the other direccion
                if self.matrix[index_row][index_col].is_piece_inside() and self.matrix[index_row][index_col].get_piece().pieces_is_queen():
                    test_coordinates['change_y'] *= -1
                    forced = self.add_forced_movements(test_coordinates,playing,forced)
                index_col += 1
            index_row += 1
        return forced
    
    #Method to add the forced elements
    def add_forced_movements(self,test_coordinates,playing,forced):
        #Establish the possible positions where to move
        coordinates = {
            'from_x': test_coordinates['index_col'],
            'from_y': test_coordinates['index_row'],
            'to_x': test_coordinates['index_col'] + 2,
            'to_y': test_coordinates['index_row'] + test_coordinates['change_y']
        }
        dif_dir = self.difference_between_and_direction(coordinates)
        
        #Check if this movement should be added
        if self.can_add_forced_movements(coordinates,playing,dif_dir):
            forced.append([coordinates])

        #Establish the possible positions where to move   
        coordinates2 = {
            'from_x': test_coordinates['index_col'],
            'from_y': test_coordinates['index_row'],
            'to_x': test_coordinates['index_col'] - 2,
            'to_y': test_coordinates['index_row'] + test_coordinates['change_y']
        }
        dif_dir = self.difference_between_and_direction(coordinates2)

        #Check if this movement should be added
        if self.can_add_forced_movements(coordinates2,playing,dif_dir):
            forced.append([coordinates2])
        return forced

    def can_add_forced_movements(self,coordinates,playing,dif_dir):
        if self.verify_moves(coordinates,playing,dif_dir):
            return self.piece_can_eat(coordinates,playing,dif_dir)
        return False
                
    #Method to verify if the piece can eat
    def piece_can_eat(self,coordinates,playing,dif_dir):
        if self.matrix[coordinates['to_y'] - dif_dir['dir_y']][coordinates['to_x'] - dif_dir['dir_x']].is_piece_inside():
            return self.matrix[coordinates['to_y'] - dif_dir['dir_y']][coordinates['to_x'] - dif_dir['dir_x']].get_piece() not in playing.get_list_pieces()
        return False
    
    #Method to return the movements in which the piece can eat after eating
    def piece_can_eat_after_eat(self,from_x,from_y,playing):
        moves = []
        coordinates = {
            'from_x': from_x,
            'from_y': from_y,
            'to_x': from_x +2,
            'to_y': from_y +2
        }
        moves = self.condition_to_eat_after_eat(coordinates,playing,moves)
        coordinates['to_x'] = from_x +2
        coordinates['to_y'] = from_y -2
        moves = self.condition_to_eat_after_eat(coordinates,playing,moves)
        coordinates['to_x'] = from_x -2
        coordinates['to_y'] = from_y +2
        moves = self.condition_to_eat_after_eat(coordinates,playing,moves)
        coordinates['to_x'] = from_x -2
        coordinates['to_y'] = from_y -2
        moves = self.condition_to_eat_after_eat(coordinates,playing,moves)
        return moves
    
    #Method to add to the arrangement movements that meet the condition of eating after eating
    def condition_to_eat_after_eat(self,coordinates,playing,moves):
        dif_dir = self.difference_between_and_direction(coordinates)
        if self.verify_moves(coordinates,playing,dif_dir):
            if self.piece_can_eat(coordinates,playing,dif_dir):
                moves.append([coordinates])
        return moves

    #Method to return the matrix
    def get_matrix(self):
        return self.matrix
    
    #Method to determine if the coordinates are within the range of the matrix
    def coordinates_is_in_range(self,coordinates):
        for coor in coordinates:
            if 0 > coordinates[coor] or  coordinates[coor] >= 8:
                return False
        return True

    #Method that returns the difference between two numbers
    def difference_between(self,a,b):
        return a - b if a > b else b -a
    
    #Method that returns the direction of movement
    def direction(self,a,b):
        return -1 if a > b else +1

    #Method that returns the difference between two numbers and the direction of movement
    def difference_between_and_direction(self,coordinates):
        dir_dif = {
            'dif_x': self.difference_between(coordinates['from_x'],coordinates['to_x']),
            'dif_y': self.difference_between(coordinates['from_y'],coordinates['to_y']),
            'dir_x': self.direction(coordinates['from_x'],coordinates['to_x']),
            'dir_y': self.direction(coordinates['from_y'],coordinates['to_y'])
        }
        return dir_dif
    
    def become_queen(self,playing,coordinates):
        return coordinates['to_y'] == 0 if playing.get_player_dir() == -1 and not self.matrix[coordinates['to_y']][coordinates['to_x']].get_piece().pieces_is_queen() else coordinates['to_y'] == self.size_m -1