# imports
from pygame import *
import engine

init()
# constants
WIDTH = 800
HEIGHT = 800
DIMENSIONS = 8
SQUARE_SIZE = (HEIGHT // DIMENSIONS)
FPS = 30
IMGS = {}

def main():
    game_screen = display.set_mode((WIDTH, HEIGHT))
    clock = time.Clock()
    game_screen.fill(Color(120, 112, 235, 255))
    # get access to the game class
    game_state = engine.Game()
    valid_moves = game_state.get_valid_moves()
    move_is_made = False
    animate = False
    loading_images()
    run = True
    selected_square = ()
    players_clicks = []
    while run:
        for eve in event.get():
            if eve.type == QUIT:
                run = False
            elif eve.type == MOUSEBUTTONDOWN:
                location = mouse.get_pos()
                row = location[1] // SQUARE_SIZE
                col = location[0] // SQUARE_SIZE
                if selected_square == (row, col):
                    selected_square = ()
                    players_clicks = []
                else:
                    selected_square = (row, col)
                    players_clicks.append(selected_square)
                if len(players_clicks) == 2:
                    move = engine.MovePiece(players_clicks[0], players_clicks[1], game_state.board)
                    print(move.create_notation())
                    for i in range(len(valid_moves)):
                        if move == valid_moves[i]:
                            game_state.make_move(valid_moves[i])
                            move_is_made = True
                            animate = True
                            selected_square = ()
                            players_clicks = []
                    if not move_is_made:
                        players_clicks = [selected_square]
            elif eve.type == KEYDOWN:
                if eve.key == K_SPACE:
                    game_state.undo_move()
                    move_is_made = True
                    animate = False
                elif eve.key == K_r:
                    game_state = engine.Game()
                    valid_moves = game_state.get_valid_moves()
                    selected_square = ()
                    players_clicks = []
                    move_is_made = False
                    animate = False

        if move_is_made:
            if animate: 
                animate_move(game_state.movesLogs[-1], game_screen, game_state.board, clock)
            valid_moves = game_state.get_valid_moves()
            move_is_made = False
            animate = False

        draw_game(game_screen, game_state, valid_moves, selected_square)
        clock.tick(FPS)
        display.flip()

def highlight_squares(screen, game_state, valid_moves, sq_selected):
    if sq_selected != ():
        row, col = sq_selected
        if game_state.board[row][col][0] == ("w" if game_state.whiteMove else "b"):
            surf = Surface((SQUARE_SIZE, SQUARE_SIZE))
            surf.set_alpha(150)
            surf.fill(Color(0, 255, 155, 255))
            screen.blit(surf, (col*SQUARE_SIZE, row*SQUARE_SIZE))

            surf.fill(Color(255, 200, 0, 255))
            for move in valid_moves:
                if move._start_row == row and move._start_col == col:
                    screen.blit(surf, (SQUARE_SIZE*move._end_col, SQUARE_SIZE*move._end_row))

def loading_images():
    pieces_array = ['bB', 'bK', 'bN', 'bP', 'bR', 'bQ',
                    'wB', 'wK', 'wN', 'wP', 'wR', 'wQ']
    # iterate through pieces_array and load the into the IMGS hashmap
    for piece in pieces_array:
        IMGS[piece] = transform.scale(image.load("chess_game/pieces/" + piece + ".png"), (SQUARE_SIZE, SQUARE_SIZE))

def draw_game(game_screen, game_state, valid_moves, sq_selected):
    draw_board(game_screen)
    highlight_squares(game_screen, game_state, valid_moves, sq_selected)
    draw_pieces(game_screen, game_state.board)

def draw_board(game_screen):
    global colors
    colors = [Color(255, 255, 255, 255), Color(73, 158, 215, 255)]
    for row in range(DIMENSIONS):
        for col in range(DIMENSIONS):
            piece_color = colors[(row + col) % 2]
            draw.rect(game_screen, piece_color, Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))



def draw_pieces(game_screen, board):
    for row in range(DIMENSIONS):
        for col in range(DIMENSIONS):
            piece = board[row][col] 
            if piece != "--":
                game_screen.blit(IMGS[piece], Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def animate_move(move, screen, board, clock):
    global colors
    coordinates = []
    dr, dc = move._end_row - move._start_row, move._end_col - move._start_col
    frames_per_square = 12
    frame_count = (abs(dr) + abs(dc)) * frames_per_square
    for frame in range(frame_count + 1):
        row, col = (move._start_row + dr * frame/frame_count, move._start_col + dc * frame/frame_count)
        draw_board(screen)
        draw_pieces(screen, board)
        color = colors[(move._end_row + move._end_col) % 2]
        end_square = Rect(move._end_col * SQUARE_SIZE, move._end_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        draw.rect(screen, color, end_square)
        if move._piece_captured != "--":
            screen.blit(IMGS[move._piece_captured], end_square)
        screen.blit(IMGS[move._piece_moved], Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main()