"""
Our main driver file, handling user info and displaying the current gamestate
"""
import pygame as p
import ChessEngine
import winsound


WIDTH = HEIGHT = 512
DIMENSION = 8 # dimension chest board are 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15 # for animation later on
IMAGES = {}   #techniaclly already full of images after we start our main function

"""
initialize a global dictionary of images. this will be called exactly once in the main
"""
def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE)) #uploads each image as a VALUE
    # Note: we can accses an image by saying 'IMAGES['WP'] for example. (the images are the values)

"""
the main driver for our code. this will handle user input and updating the graphics
"""

def main():
    p.display.set_caption("Ohad's_chess_game")
    icon = p.image.load(r"C:\Users\shine\OneDrive\Desktop\myimage.png")
    p.display.set_icon(icon)
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))  # displaying a 8 x 8 window white screen
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()   # מופע של המחלקה chess engine
    validMoves = gs.getValidMoves() # list of valid moves to check later on if the move is valid
    moveMade = False # flag variable for when a move is made
    animate = False # flag variable for when we should animate a move
    loadImages() # only doing this once, before the while loop   (already loaded once we start the main function)
    running = True
    sqSelected = () # no square is selected, keep track of the last click of the user (tuple: (row, cow))
    playerClicks = [] # keep track of player clicks two tuples: [(6, 4), (4, 4)]
    gameOver = False
    playBackgroundMusic()
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver: # conidition so that if gave is not over, then allow everything else to work
                    location = p.mouse.get_pos() # (x, y) location of mouse
                    col = location[0] // SQ_SIZE     # determines the position of the X
                    row = location[1] // SQ_SIZE  # determines the position of the Y
                    if sqSelected == (row, col): # condition to check if we clicked on the same place twice (sqSelected keeps track of the last click always)
                        sqSelected = ()  # resets and clears
                        playerClicks = []  # resets and clears
                    else:
                        sqSelected = (row, col) # (x , y)
                        playerClicks.append(sqSelected)   # append position of both the first and the last clicks.
                    if len(playerClicks) == 2:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board) # מופע ! playerclicks = רשימה עם tuples
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]: # checks to see if the move (the clicks) are the same move that are in the list of validmoves
                                gs.makeMove(validMoves[i]) # makes the move generated by the engine
                                Chess_Music()
                                moveMade = True
                                animate = True
                                sqSelected = () # reset the clicks
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected] # quality of life for when I decide to move another piece after I already clicked on a piece ( de-select )

            # key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: # undo when Z is pressed
                    gs.undoMove()
                    moveMade = True
                    animate = False
                if e.key == p.K_r: # reset the board when "r" is pressed
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False

        if moveMade: # if a move was made, we need to generate a new valid moves for the next move (say I played pawn and then played Bishop for example)
            if animate:
                animateMove(gs.movelog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected)        # starts the drawgamestate function below which starts the drawboard function below it

        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, "Black wins by checkmate")
            else:
                drawText(screen, "White wins by checkmate")
        elif gs.staleMate:
            gameOver = True
            drawText(screen, "Stalemate")

        clock.tick(MAX_FPS)
        p.display.flip()



"""
hightlights the square selected and moves for the piece selected
"""
def hightlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected # (r, c) = (x, y) # first click
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'): # sqselected is a piece that can be moved
            #hightlight seleceted square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100) # transperancy value -> 0 transparent, 255 is none transparent
            s.fill(p.Color("blue"))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE)) # position of the hightlight ( the same x, y of the position of the square selected)
            #hightlight moves from that square
            s.fill(p.Color("green"))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))


"""
responsible for all the graphics within a current game state.
"""
def drawGameState(screen, gs, validMoves, sqSelected):    # gs = מופע של המחלקה מצב המשחק שנקרא למתודה במחלקה בהמשך הפונקציה (ChessEngine.Gamestate())
    drawBoard(screen) # draw the squares on the board
    hightlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board) # draw the pieces on top of the squares

"""
draw the suqares on the board. the top left square is always light.
"""
def drawBoard(screen):
    global colors
    colors = [p.Color("White"), p.Color("gray")]
    for r in range(DIMENSION):   # r = from left to right (row)
        for c in range(DIMENSION):   # c = UP and DOWN (column)
            color = colors[(r+c) % 2]    # this decides which color the square is (even = white, uneven = gray)
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE)) # draws the square on the board rect(surface, color, placement and size)
"""
draw pieces on the board using the current GameState.board
"""
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]   # board[r][c] = one of the string pieces in the self.board (__init___) from our gameState
            if piece != "--": # if it's not an empty square
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE)) # puts down the pieces images on the board,
                                                                     # each piece is determined by a key from our dicitionary at the top



def rectest(screen):   # test will delete later.
    p.draw.rect(screen, p.Color("black"), p.Rect(0, 0, SQ_SIZE, SQ_SIZE))
    p.draw.rect( screen, p.Color( "red" ), p.Rect( SQ_SIZE, 2 * SQ_SIZE, SQ_SIZE, SQ_SIZE ) )
    p.draw.rect( screen, p.Color( "black" ), p.Rect( 2 * SQ_SIZE, 2 * SQ_SIZE, SQ_SIZE, SQ_SIZE ) )

"""
animating a move
"""
def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow # distance
    dC = move.endCol - move.startCol # distance
    framesPerSquare = 10 # frames to move one square
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare # counts how many squares for each move if it's 7/7 -> 6/6 it's just one square for example
    for frame in range(frameCount + 1): # one square = 10 frames
        r, c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount) # frames if say I moved 2 squares -> 1/20 -> 2/20 etc etc in position (x+x\\ 20, y+ y\\20) -> etc etc
        drawBoard(screen)
        drawPieces(screen, board)
        # erase the piece moved from it's ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        #draw the captured piece onto the rectangle
        if move.pieceCaptured != "--":
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # draw the moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE)) # drawng the image as it moves frame per frame
        p.display.flip()
        clock.tick(144)

def drawText(screen, text):
    font = p.font.SysFont("Times", 48, True, False)
    textObject = font.render(text, 0, p.Color("Black"))
    textlocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textlocation)
    textObject = font.render(text, 0, p.Color("blue"))
    screen.blit(textObject, textlocation.move(2, 2))


def playBackgroundMusic():
    p.mixer.init()
    p.mixer.music.load(r"C:\Users\shine\Downloads\Chess_winning_music.mp3")
    p.mixer.music.play(-1)

def Chess_Music():
    p.mixer.init()
    p.mixer.music.load(r"C:\Users\shine\Downloads\chess_sound.wav")
    p.mixer.music.play()

if __name__ == "__main__":
    main()


