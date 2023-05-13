"""
this class is responsible for storing all the information about the current stage of a chess game.
it's also responsible for determining the valid moves at the current state. it will also keep a move log.
"""
import pygame as p
class GameState():
    def __init__(self):
        # board is an 8x8 2d list, each element of the list has 2 characters.
        # the first character represent the color of the piece 'b' or 'w'
        # the 2nd character represent the type of the piece 'k' 'Q' 'R' 'b' 'n' 'p'
        # the "--" represent an empty space with no pieces.
        self.board = [          # this is a one big list with row lists inside of it
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves} # dictionary to call on a piece function by his key
        self.whiteToMove = True  # white's turn
        self.movelog = []  # list contains something like that [(x, y), (x, y), "board"] = one iteration
        self.WhiteKnightLocation = (7, 4)
        self.BlackKnightLocation = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.enpassantPossible = () # coordinates for the square where en passant capture is possible

    # takes a move as a parameter and excutes it ( this will not work for castling, and en-passant, pawn promotion)
    def makeMove(self, move):   # move = מופע של Move ?  יש שימוש במשתנים שנמצאים בקלאס של התזוזה הגדולה
        self.board[move.startRow][move.startCol] = "--"  # once a piece left his square, the square becomes empty hence "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved  # the moved piece in his new position
        self.movelog.append(move) # log the move so we can undo it later or display the history of the logs
        self.whiteToMove = not self.whiteToMove # swap players (white to black) for example.
            # updates the kings location
        if move.pieceMoved == 'wK':
            self.WhiteKnightLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.BlackKnightLocation = (move.endRow, move.endCol)

        # pawn promotion
        if move.isPawnPromotion: # checks to see if the pawn has reached the end of the board and if it's a pawn ( returns true)
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'  # color of the piece plus a queen so pawn promotes to a queen

        # en passant move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--' # capturing the pawn

        # update enpassantPossible variable
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2: # only on two square pawn advances
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()



    """
    undo the last move made
    """
    def undoMovee(self): # my way # not being used
        if len(self.movelog) != 0: # make sure that there is a move to undo TODO: done it in my own way (video part 3, time 5:40) for the guider way
            self.board[self.movelog[-1].startRow][self.movelog[-1].startCol] = self.movelog[-1].pieceMoved # '--'
            self.board[self.movelog[-1].endRow][self.movelog[-1].endCol] = self.movelog[-1].pieceCaptured # 'wK'
            self.movelog = self.movelog[:-1]  # removes the last registered movement from the list (so we can undoMoves multiple times instead of just once)
            self.whiteToMove = not self.whiteToMove




    def undoMove(self): # guide's way
        if len(self.movelog) != 0: # make sure that there is a move to undo
            move = self.movelog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            #update the king's location
            if move.pieceMoved == 'wK':
                self.WhiteKnightLocation = (move.startRow, move.startCol)
                print(self.WhiteKnightLocation)
            elif move.pieceMoved == 'bK':
                self.BlackKnightLocation = (move.startRow, move.startCol)
            # undo the en passant move
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = "--" # leave the landing square blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)
            # undo a 2 square pawn advance
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()


    """
    ALL moves considering checks
    """
    def getValidMoves(self):
        tempEnPassantPossible = self.enpassantPossible
        #1) generate all possible moves
        moves = self.getAllPossibleMoves() # list of possible moves [(x, y), (x, y), self.board] .. ..
        #2 for each move, make the move
        for i in range(len(moves)-1, -1, -1):
            self.makeMove(moves[i]) # everytime I make a move it changes turn
            #3) generate all opponent's moves
            #4) for each of your opponent's moves, see if they attack your king
            self.whiteToMove = not self.whiteToMove # swapped turns
            if self.inCheck(): # if there's a check
                moves.remove(moves[i]) # 5) if they do attack your king, not a valid move (removes that ONE move)
            self.whiteToMove = not self.whiteToMove # whenever we check we swap places so this here is to swap the turns back again
            self.undoMove() #
        if len(moves) == 0: # either checkmate or stalemate. after all the conidition filters if there is no move available to do it's (checkmate or stalemate)
            if self.inCheck(): # checks to see if the king can be captured aka checkmate
                self.checkMate = True
            else:              # if the king is not captured but there are no moves to make it's staleMate
                self.staleMate = True
        else: # condition for when we make a move and it's checkmate but then we undo the move
            self.checkMate = False
            self.staleMate = False

        self.enpassantPossible = tempEnPassantPossible
        return moves


    """
    determine if the current player is in check
    """
    def inCheck(self):
        if self.whiteToMove: # if white turn to move
            return self.squareUnderAttack(self.WhiteKnightLocation[0], self.WhiteKnightLocation[1]) # returns true or false if the king is under attack
        else:                # black turn's
            return self.squareUnderAttack(self.BlackKnightLocation[0], self.BlackKnightLocation[1]) #  returns true or false if the king is under attack

    """
    determine if the enemy can attack the square r, c
    """
    def squareUnderAttack(self, r, c): # for example r, c is the position of a king under attack
        self.whiteToMove = not self.whiteToMove # switch to the opponent's turn
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove  # we switched turns to check at the start opp moves ( so we switching back)
        for move in oppMoves:
            if move.endRow == r and move.endCol == c: #if one of the oppmoves can be positioned on a king
                return True # true if the king is under attack
        return False # false if the king is NOT under attack



    """
    All moves without considering checks
    """
    def getAllPossibleMoves(self): # goes with a for loop iterates over all the positions in the current board
        moves = []  # each item in this list will be [Move((x, y), (x, y), self.board)]
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]   # turn = "w" or "b"
                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove): # TODO: I used OR, guider used AND
                    piece = self.board[r][c][1]   # piece = "King" or "Bishop" or "Queen" etc etc..
                    self.moveFunctions[piece](r, c, moves) # gets all possible moves for that piece (dicitionary being used at the top to call at said piece function ('p' = getPawnMoves) for example
        return moves

    """
    get all the pawn moves for the pawn located at row, col and add these moves to the list
    """
    def getPawnMoves(self, r, c, moves):  # the r, c, moves = [] are being used from the function above ^
        if self.whiteToMove:# white pawn turn
            if self.board[r-1][c] == "--":  # 1 square pawn advance (checks to see if the up square is empty )
                moves.append(Move((r, c), (r-1, c), self.board)) # adds the move to the list of valid moves above
                if r == 6 and self.board[r-2][c] == "--": # if the pawn at his starting location (row = 6) and two square up is empty
                    moves.append(Move((r, c), (r-2, c), self.board))
            if c - 1 >= 0: # capture to the left
                if self.board[r-1][c-1][0] == "b": # enemy piece to capture
                    moves.append(Move((r, c), (r-1, c-1), self.board))
                elif (r-1, c-1) == self.enpassantPossible: # enpassantpossible = tuple (x, y)
                    moves.append(Move((r, c), (r-1, c-1), self.board, isEnpassantMove=True))
            if c + 1 <= 7: # capture to the right
                if self.board[r-1][c + 1][0] == "b": # enemy piece to capture
                    moves.append(Move((r, c), (r-1, c+1), self.board))
                elif (r-1, c+1) == self.enpassantPossible:  # enpassantpossible = tuple (x, y)
                    moves.append(Move((r, c), (r-1, c+1), self.board, isEnpassantMove=True))
        else: # Black's turn to move
            if self.board[r+1][c] == "--": # moves forward once square
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == "--": # moves forward 2nd square
                    moves.append(Move((r, c), (r+2, c), self.board))
            if c + 1 <= 7:  # capture to the right
                if self.board[r+1][c+1][0] == "w": # enemy piece to capture
                    moves.append(Move((r, c), (r+1, c+1), self.board))
                elif (r+1, c+1) == self.enpassantPossible: # enpassantpossible = tuple (x, y)
                    moves.append(Move((r, c), (r+1, c+1), self.board, isEnpassantMove=True))
            if c - 1 >= 0: # capture to the left
                if self.board[r+1][c-1][0] == "w": # enemy piece to capture
                    moves.append(Move((r, c), (r+1, c-1), self.board))
                elif (r+1, c-1) == self.enpassantPossible: # enpassantpossible = tuple (x, y)
                    moves.append(Move((r, c), (r+1, c-1), self.board, isEnpassantMove=True))
    """
    get all the rook moves for the rook located at row, col and add these moves to the list
    """
    def getRookMoves(self, r, c, moves):
        enemyColor = "b" if self.whiteToMove else "w"
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1)) # up, left , down, right (r, c)
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i # ( starting row + direction * square ) = row number
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: # on board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--": # empty space valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor: # either 'b' or 'w'
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break # breaks the 2nd loop and then goes on to another direction (breaks inner loop)
                    else: # friend piece invalid ( to not jump over friendly pieces or capture them)
                        break
                else: # off board
                    break

    """
    get all the knight moves for the knight located at row, col and add these moves to the list
    """
    def getKnightMoves(self, r, c, moves):
        enemyColor = "b" if self.whiteToMove else "w" # row is left right, coln is up down ?
        direction = {"UP_LEFT" :(r-2, c-1), "UP_RIGHT" :(r-2, c+1), "LEFT_UP" :(r-1, c-2), "LEFT_DOWN" :(r+1, c-2), "RIGHT_UP" :(r-1, c+2),
                      "RIGHT_DOWN": (r+1, c+2), "DOWN_LEFT": (r+2, c-1), "DOWN_RIGHT": (r+2, c+1)}
        for key, value in direction.items():
            if (0 <= direction[key][0] <= 7 and 0 <= direction[key][1] <= 7) and\
                    ((self.board[value[0]][value[1]][0] == enemyColor) or (self.board[value[0]][value[1]] == "--")):
                moves.append(Move((r, c), (value[0], value[1]), self.board))
            # the conidition above is to check if the endpiece is within the limit of the board and then if the endpiece is an enemy or an empty space
            # that way it won't capture friendly pieces.
            # Knight can skip through pieces so it made the job a bit easier for us

    """
    get all the Bishop moves for the bishop located at row, col and add these moves to the list
    """
    def getBishopMoves(self, r, c, moves):
        enemyColor = "b" if self.whiteToMove else "w"
        directions = ((1, -1), (1, 1), (-1, -1), (-1, 1)) # down left , down right, up left, up right
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i # starting row + end row times square = end x number
                endCol = c + d[1] * i # starting col + end col times square = end y number
                if 0 <= endRow <= 7 and 0 <= endCol <= 7: # check to see that it's within the board limit
                    endMove = self.board[endRow][endCol]    # located the end piece
                    if endMove == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endMove[0] == enemyColor: # if the end piece is 'b' or 'w'
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break # breaks once it sees there is an enemy piece ( so we won't jump above it)
                    else:
                        break # breaks once it sees friendly piece
                else: # conidition for a break if it's out of board
                    break

    """
    get all the Queen moves for the queen located at row, col and add these moves to the list
    """
    def getQueenMoves(self, r, c, moves): # queen is a bishop & rook combined (techniaclly can put self.getRookMoves & self.getBishopMoves)
        enemyColor = "b" if self.whiteToMove else "w"
        directions = ((1, -1), (1, 1), (-1, -1), (-1, 1), (-1, 0), (1, 0), (0, -1), (0, 1))
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i # starting row + end row times square = end x number
                endCol = c + d[1] * i # starting col + end col times square = end y number
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                    endpiece = self.board[endRow][endCol]
                    if endpiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endpiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break # breaks once it sees there is an enemy piece ( so we won't jump above it)
                    else:
                        break # breaks once it sees friendly piece
                else: # conidition for a break if it's out of board
                    break



    """
    get all the king moves for the king located at row, col and add these moves to the list
    """
    def getKingMoves(self, r, c, moves):
        enemyColor = "b" if self.whiteToMove else "w"
        directions = {"UP_LEFT": (r - 1, c - 1), "UP_RIGHT": (r - 1, c + 1), "LEFT": (r, c - 1), "LEFT_DOWN": (r + 1, c - 1),
                      "DOWN": (r - 1, c), "DOWN_right": (r + 1, c + 1), "RIGHT": (r, c + 1), "UP": (r-1, c)}
        for key, value in directions.items():
            if (0 <= value[0] <= 7 and 0 <= value[1] <= 7) and ((self.board[value[0]][value[1]][0] == enemyColor) or (self.board[value[0]][value[1]] == "--")):
                moves.append(Move((r, c), (value[0], value[1]), self.board))

class Move():
    # maps keys to values
    # key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,   # reminder that our positional is 0,0 top left (where right is Y and bottom is X)
                   "5": 3, "6":2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}   # swapped keys and values to match a real chess positionals (A,8 b,7 ... ) etc
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}
                    # startsq = (x, y) endsq = (x, y) board = big string above
    def __init__(self, startsq, endsq, board, isEnpassantMove=False):  # start square and end square are tuples (first and last click) boards stands for board state
        self.startRow = startsq[0]    # coordinates the X
        self.startCol = startsq[1]    # coordinates the Y
        self.endRow = endsq[0]        #     same
        self.endCol = endsq[1]        #     same
        self.pieceMoved = board[self.startRow][self.startCol]  # could be any piece (king , queen, knight etc.. or even an empty space)
        self.pieceCaptured = board[self.endRow][self.endCol]
        # pawn promotion
        self.isPawnPromotion = False
        if (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7): # checks to see if the pieceMoved is a pawn and if it reached the end board
            self.isPawnPromotion = True # if the pawn reached the end board, returns true for pawn promotion
        # en passant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'



        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol # generates a move ID (each ID is unique) used for the __eq__ method below TODO: figure out a way to make it better and cleaner




    """
    overriding the equals method 
    """
    def __eq__(self, other):    # since we can't check if an object equals to another object (object(Move) == object(Move) for example, with this method we will be able to
        if isinstance(other, Move): # checks if both of them are objects (other stands for the other object), (Move stands object)
            return self.moveID == other.moveID   # returns True
        return False  # returns False

    def getChessNotation(self):   # allows us to see what the move is (A8 >>> B5) for example. always a string
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)  # this is two tuples ( start move) (end move)
                                                                                                            # for example (a, 8) >> (b, 5)
    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]   # example is "A8" or "B5" etc always a string  so if my tuple is (0, 0) it will give me (a, 8)









