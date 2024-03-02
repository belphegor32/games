# game class
class Game():
    def __init__(self):
        self.whiteMove = True
        self.movesLogs = []
        self.white_king_loc = (7, 4)
        self.black_king_loc = (0, 4)
        self.in_check = False
        self.pins = []
        self.checks = []
        self.enpassant_possbile = ()
        self.current_castling_rights = CastlingRights(True, True, True, True)
        self.castle_rights_logs = [CastlingRights(self.current_castling_rights.wks, self.current_castling_rights.bks, 
                                                  self.current_castling_rights.wqs, self.current_castling_rights.bqs)]
        self.moveFunctions = {'P': self.get_pawn_moves,
                              'R': self.get_rook_moves,
                              'N': self.get_knight_moves,
                              'Q': self.get_queen_moves,
                              'K': self.get_king_moves,
                              'B': self.get_bishop_moves} 
        
        # innit the board
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'],
        ]

    def make_move(self, move):
        self.board[move._end_row][move._end_col] = move._piece_moved
        self.board[move._start_row][move._start_col] = "--"
        self.movesLogs.append(move) 
        self.whiteMove = not self.whiteMove
        if move._piece_moved == "wK":
            self.white_king_loc = (move._end_row, move._end_col)
        elif move._piece_moved == "bK":
            self.black_king_loc = (move._end_row, move._end_col)

        if move.is_pawn_promotion:
            self.board[move._end_row][move._end_col] = move._piece_moved[0] + "Q"    
        
        if move.is_enpassant:
            self.board[move._start_row][move._end_col] = "--"

        if move._piece_moved[1] == "P" and abs(move._start_row - move._end_row) == 2:
            self.enpassant_possbile = ((move._start_row + move._end_row)//2, move._start_col)
        else:
            self.enpassant_possbile = ()

        if move.is_castle_move:
            if move._end_col - move._start_col == 2:
                self.board[move._end_row][move._end_col - 1] = self.board[move._end_row][move._end_col + 1]
                self.board[move._end_row][move._end_col + 1] = "--"
            else:
                self.board[move._end_row][move._end_col + 1] = self.board[move._end_row][move._end_col - 2]
                self.board[move._end_row][move._end_col - 2] = "--"
        
        self.update_castle_rights(move)
        self.castle_rights_logs.append(CastlingRights(self.current_castling_rights.wks, self.current_castling_rights.bks, 
                                                  self.current_castling_rights.wqs, self.current_castling_rights.bqs))
    

    def update_castle_rights(self, move):
        if move._piece_moved == "wK":
            self.current_castling_rights.wks = False
            self.current_castling_rights.wqs = False
        elif move._piece_moved == "bK":
            self.current_castling_rights.bks = False
            self.current_castling_rights.bqs = False
        elif move._piece_moved == "wR":
            if move._start_row == 7:
                if move._start_col == 0:
                    self.current_castling_rights.wqs = False
                elif move._start_col == 7:
                    self.current_castling_rights.wks = False
        elif move._piece_moved == "bR":
            if move._start_row == 0:
                if move._start_col == 0:
                    self.current_castling_rights.bqs = False
                elif move._start_col == 7:
                    self.current_castling_rights.bks = False

    def undo_move(self):
        if len(self.movesLogs) != 0:
            move = self.movesLogs.pop()
            self.board[move._start_row][move._start_col] = move._piece_moved
            self.board[move._end_row][move._end_col] = move._piece_captured
            self.whiteMove = not self.whiteMove
            if move._piece_moved == "wK":
                self.white_king_loc = (move._start_row, move._start_col)
            elif move._piece_moved == "bK":
                self.black_king_loc = (move._start_row, move._start_col)
            
            if move.is_enpassant:
                self.board[move._end_row][move._end_col] = "--"
                self.board[move._start_row][move._end_col] = move._piece_captured
                self.enpassant_possbile = (move._end_row, move._end_col)
            
            if move._piece_moved[1] == "P" and abs(move._start_row - move._end_row) == 2:
                self.enpassant_possbile = ()
            
        self.castle_rights_logs.pop()
        self.current_castling_rights = self.castle_rights_logs[-1]
        
        if move.is_castle_move:
            if move._end_col - move._start_col == 2:
                self.board[move._end_row][move._end_col + 1] = self.board[move._end_row][move._end_col - 1]
                self.board[move._end_row][move._end_col - 1] = "--"
            else:
                self.board[move._end_row][move._end_col - 2] = self.board[self._end_row][move._end_col + 1]
                self.board[move._end_row][move._end_col + 1] = "--"


    def get_valid_moves(self):
        moves = []
        self.in_check, self.pins, self.checks = self.check_for_pins_and_checks()

        if self.whiteMove:
            king_row = self.white_king_loc[0]
            king_col = self.white_king_loc[1]
        else:
            king_row = self.black_king_loc[0]
            king_col = self.black_king_loc[1]


        if self.in_check:
            if len(self.checks) == 1:
                moves = self.all_possible_moves()
                check = self.checks[0]
                check_row = check[0]
                check_col = check[1]
                piece_checking = self.board[check_row][check_col]
                valid_squares = []
                if piece_checking[1] == "N":
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(1, 8):
                        valid_square = (king_row + check[2] * i, king_col + check[3] * i)
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_col:
                            break
                
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i]._piece_moved[1] != "K":
                        if not (moves[i]._end_row, moves[i]._end_col) in valid_squares:
                            moves.remove(moves[i])
            else:
                self.get_king_moves(king_row, king_col, moves)
        else:
            moves = self.all_possible_moves()
        
        if self.whiteMove:
            self.get_castle_moves(self.white_king_loc[0], self.white_king_loc[1], moves, "w")
        else:
            self.get_castle_moves(self.black_king_loc[0], self.black_king_loc[1], moves, "b")
        
        return moves
                

    def king_in_check(self):
        if self.whiteMove:
            return self.sq_under_attack(self.white_king_loc[0], self.white_king_loc[1])
        else:
            return self.sq_under_attack(self.black_king_loc[0], self.black_king_loc[1])
    
    def sq_under_attack(self, row, col):
        self.whiteMove = (not self.whiteMove)
        opponent_moves = self.all_possible_moves()
        self.whiteMove = (not self.whiteMove)
        for move in opponent_moves:
            if move._end_row == row and move._end_col == col:
                return True
        return False

    def all_possible_moves(self):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[0])):
                cur_turn = self.board[row][col][0]
                if (cur_turn == "w" and self.whiteMove == True) or (cur_turn == "b" and not self.whiteMove):
                    piece = self.board[row][col][1]
                    self.moveFunctions[piece](row, col, moves)

        return moves
    
    def get_pawn_moves(self, row, col, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteMove == True:
            if self.board[row - 1][col] == "--":
                if not piece_pinned or pin_direction == (-1, 0):
                    moves.append(MovePiece((row, col), (row - 1, col), self.board))
                    if row == 6 and self.board[row - 2][col] == "--":
                        moves.append(MovePiece((row, col), (row - 2, col), self.board))
            
            if col - 1 >= 0:
                if self.board[row - 1][col - 1][0] == "b":
                    if not piece_pinned or pin_direction == (-1, -1):
                        moves.append(MovePiece((row,col), (row-1,col-1), self.board))
                elif (row - 1, col - 1) == self.enpassant_possbile:
                    moves.append(MovePiece((row,col), (row-1,col-1), self.board, is_enpassant=True))

            if col + 1 <= 7:
                if self.board[row - 1][col + 1][0] == "b":
                    if not piece_pinned or pin_direction == (-1, 1):
                        moves.append(MovePiece((row,col), (row-1,col+1), self.board))
                elif (row - 1, col + 1) == self.enpassant_possbile:
                    moves.append(MovePiece((row,col), (row-1,col+1), self.board, is_enpassant=True))    
        else:
            if self.board[row + 1][col] == "--":
                if not piece_pinned or pin_direction == (1, 0):
                    moves.append(MovePiece((row,col), (row+1,col), self.board))
                    if row == 1 and self.board[row + 2][col] == "--":
                        moves.append(MovePiece((row,col), (row+2, col), self.board))
            
            if col - 1 >= 0:
                if self.board[row + 1][col - 1][0] == "w":
                    if not piece_pinned or pin_direction == (1, -1):
                        moves.append(MovePiece((row,col), (row+1,col-1), self.board))
                elif (row + 1, col - 1) == self.enpassant_possbile:
                    moves.append(MovePiece((row,col), (row+1,col-1), self.board, is_enpassant=True))
            if col + 1 <= 7:
                if self.board[row + 1][col + 1][0] == "w":
                    if not piece_pinned or pin_direction == (1, 1):
                        moves.append(MovePiece((row,col), (row+1,col+1), self.board))
                elif (row + 1, col + 1) == self.enpassant_possbile:
                    moves.append(MovePiece((row,col), (row+1,col+1), self.board, is_enpassant=True))

    def get_rook_moves(self, row, col, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[row][col][1] != "Q":
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemy_color = "b" if self.whiteMove else "w"

        for d in directions:
            for i in range(1, 8):
                end_row = row + d[0] * i
                end_col = col + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--":
                            moves.append(MovePiece((row, col), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:
                            moves.append(MovePiece((row, col), (end_row, end_col), self.board))
                            break
                        else:
                            break
                    else:
                        break

    def get_queen_moves(self, row, col, moves):
        self.get_rook_moves(row, col, moves)
        self.get_bishop_moves(row, col, moves)

    def get_knight_moves(self, row, col, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        ally_color = "w" if self.whiteMove else "b"
        for m in knight_moves:
            end_row = row + m[0]
            end_col = col + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                if not piece_pinned:
                    end_piece = self.board[end_row][end_col][0]
                    if end_piece != ally_color:
                        moves.append(MovePiece((row, col), (end_row, end_col), self.board))



    def get_bishop_moves(self, row, col, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemy_color = "b" if self.whiteMove else "w"

        for d in directions:
            for i in range(1, 8):
                end_row = row + d[0] * i
                end_col = col + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--":
                            moves.append(MovePiece((row, col), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:
                            moves.append(MovePiece((row, col), (end_row, end_col), self.board))
                            break
                        else:
                            break
                else:
                    break

    def get_king_moves(self, row, col, moves):
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally_color = "w" if self.whiteMove else "b"
        for i in range(8):
            end_row = row + row_moves[i]
            end_col = col + col_moves[i]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:
                    if ally_color == "w":
                        self.white_king_loc = (end_row, end_col)
                    else:
                        self.black_king_loc = (end_row, end_col)
                    inCheck, pins, checks = self.check_for_pins_and_checks()
                    if not inCheck:
                        moves.append(MovePiece((row, col), (end_row, end_col), self.board))
                    
                    if ally_color == "w":
                        self.white_king_loc = (row, col)
                    else:
                        self.black_king_loc = (row, col)
    
    def get_castle_moves(self, row, col, moves, ally_color):
        if self.sq_under_attack(row, col):
            return
        if (self.whiteMove and self.current_castling_rights.wks) or (not self.whiteMove and self.current_castling_rights.bks):
            self.get_king_side_castle_moves(row, col, moves, ally_color)
        if (self.whiteMove and self.current_castling_rights.wqs) or (not self.whiteMove and self.current_castling_rights.bqs):
            self.get_queen_side_castle_moves(row, col, moves, ally_color)

    def get_king_side_castle_moves(self, row, col, moves, ally_color):
        if self.board[row][col + 1] == "--" and self.board[row][col + 2] == "--":
            if not self.sq_under_attack(row, col+1) and not self.sq_under_attack(row, col+2):
                moves.append(MovePiece((row, col), (row, col+2), self.board, is_castle_move=True))


    def get_queen_side_castle_moves(self, row, col, moves, ally_color):
        if self.board[row][col - 1] == "--" and self.board[row][col - 2] == "--" and self.board[row][col - 3] == "--":
            if not self.sq_under_attack(row, col - 1) and not self.sq_under_attack(row, col - 2):
                moves.append(MovePiece((row, col), (row, col-2), self.board, is_castle_move=True))


    def check_for_pins_and_checks(self):
        pins = []
        checks = []
        inCheck = False
        if self.whiteMove:
            enemy_color = "b"
            ally_color = "w"
            start_row = self.white_king_loc[0]
            start_col = self.white_king_loc[1]
        else:
            enemy_color = "w"
            ally_color = "b"
            start_row = self.black_king_loc[0]
            start_col = self.black_king_loc[1]
        
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possible_pins = ()
            for i in range(1, 8):
                end_row = start_row + d[0] * i
                end_col = start_col + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color and end_piece != "K":
                        if possible_pins == ():
                            possible_pins = (end_row, end_col, d[0], d[1])
                        else:
                            break
                    elif end_piece[0] == enemy_color:
                        type = end_piece[1]

                        if (0 <= j <= 3 and type == "R") or \
                            (4 <= j <= 7 and type == "B") or \
                            (i == 1 and type == "P" and ((enemy_color == "w" and 6 <= j <= 7) or (enemy_color == "b" and 4 <= j <= 5))) or \
                            (type == "Q") or (i == 1 and type == "K"):
                            if possible_pins == ():
                                inCheck = True
                                checks.append((end_row, end_col, d[0], d[1]))
                            else:
                                pins.append(possible_pins)
                                break
                        else:
                            break
                else:
                    break
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knight_moves:
            end_row = start_row + m[0]
            end_col = start_row + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == "N":
                    inCheck = True
                    checks.append((end_row, end_col, m[0], m[1]))
        return inCheck, pins, checks

class CastlingRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class MovePiece():

    def __init__(self, start_square, end_square, board, is_enpassant = False, is_castle_move = False):
        self._start_row = start_square[0]
        self._start_col = start_square[1]
        self._end_row = end_square[0]
        self._end_col = end_square[1]
        self._piece_moved = board[self._start_row][self._start_col]
        self._piece_captured = board[self._end_row][self._end_col]

        self.is_pawn_promotion = False
        if (self._piece_moved == "wP" and self._end_row == 0) or (self._piece_moved == "bP" and self._end_row == 7):
            self.is_pawn_promotion = True

        self.is_enpassant = is_enpassant
        if self.is_enpassant:
            self._piece_captured = "wP" if self._piece_moved == "bP" else "bP"
        
        self.is_castle_move = is_castle_move

        self._moveID = self._start_row * 1000 + self._start_col * 100 + self._end_row * 10 + self._end_col

    def __eq__(self, other):
        if isinstance(other, MovePiece):
            return self._moveID == other._moveID
        return False

    rank_to_row = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in rank_to_row.items()}

    file_to_col = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    col_to_file = {v: k for k, v in file_to_col.items()}

    def create_notation(self):
        return self.get_file_rank(self._start_row, self._start_col) + self.get_file_rank(self._end_row, self._end_col)

    def get_file_rank(self, row, col):
        return self.col_to_file[col] + self.rows_to_ranks[row]