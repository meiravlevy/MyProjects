/**
 * This class represents one game of Tic Tac Toe.
 * @author Meirav Levy
 */
class Game {
    /**
     * The default win streak of the game.
     */
    public static final int DEFAULT_WIN_STREAK = 3;

    private Player playerX;
    private Player playerO;
    private Renderer renderer;
    private Board board;
    private int winStreak;
    private int empty_cells;

    /**
     * constructor.
     * @param playerX player with mark symbol X.
     * @param playerO player with mark symbol O.
     * @param renderer the renderer of the board.
     */
    public Game(Player playerX, Player playerO, Renderer renderer) {
        this.playerX = playerX;
        this.playerO = playerO;
        this.renderer = renderer;
        this.board = new Board();
        this.winStreak = DEFAULT_WIN_STREAK;
        this.empty_cells = board.getSize() * board.getSize();
    }

    /**
     * Contructor.
     * @param playerX player with mark symbol X.
     * @param playerO player with mark symbol O.
     * @param size the size of the board.
     * @param winStreak the streak of same mark needed in order to win.
     * @param renderer the renderer of the board.
     */
    public Game(Player playerX, Player playerO, int size, int winStreak,
                Renderer renderer) {
        this.playerX = playerX;
        this.playerO = playerO;
        this.renderer = renderer;
        this.board = new Board(size);
        if(winStreak < 2 || winStreak > size) {
            this.winStreak = size;
        } else {
            this.winStreak = winStreak;
        }
        this.empty_cells = board.getSize() * board.getSize();
    }

    /**
     * Returns the win streak needed to win the game.
     * @return win streak needed to win the current game.
     */
    public int getWinStreak() {
        return winStreak;
    }

    /**
     * Returns the size of the board.
     * @return the size of the current game board.
     */
    public int getBoardSize() {
        return board.getSize();
    }

    /**
     * Runs one game and renders the board after each player's turn.
     * @return The mark symbol of the winner of the game. If the game ends with a tie,
     * returns BLANK mark.
     */
    public Mark run() {
        for(int i = 0; !isGameOver(); i = (i + 1) % 2 ){
            if(i % 2 == 0) {
                playerX.playTurn(board, Mark.X);
            }
            else {
                playerO.playTurn(board, Mark.O);
            }
            renderer.renderBoard(board);
            empty_cells -= 1;
        }
        return IsGameWithWinStreak();

    }
    /*
    * Returns true if the game is over and false otherwise.
    */
    private boolean isGameOver() {
        return empty_cells == 0 || IsGameWithWinStreak() != Mark.BLANK;
    }

    /*
    * Checks if there is a win streak of one of the players. If so, returns true.
    * Otherwise, returns false.
    */
    private Mark IsGameWithWinStreak() {
        Mark horizontalWinStreak = doesGameHaveHorizontalWinStreak();
        if(horizontalWinStreak != Mark.BLANK) {
            return horizontalWinStreak;
        }

        Mark verticalWinStreak = doesGameHaveVerticalWinStreak();
        if(verticalWinStreak != Mark.BLANK) {
            return verticalWinStreak;
        }

        Mark diagonalFromTopLeftWinStreak = doesGameHaveDiagonalFromTopLeftWinStreak();
        if(diagonalFromTopLeftWinStreak != Mark.BLANK) {
            return diagonalFromTopLeftWinStreak;
        }

        return doesGameHaveDiagonalFromTopRightWinStreak();
    }

    /*
    * Checks if there is a horizontal win streak of one of the players. If so, returns true.
    * Otherwise, returns false
    */
    private Mark doesGameHaveHorizontalWinStreak() {
        for(int row = 0; row < board.getSize(); row++) {
            int xWinStreak = 0;
            int oWinStreak = 0;
            for(int col = 0; col < board.getSize(); col++) {
                Mark mark = board.getMark(row, col);
                switch(mark) {
                    case X:
                        xWinStreak += 1;
                        oWinStreak = 0;
                        break;
                    case O:
                        oWinStreak += 1;
                        xWinStreak = 0;
                        break;
                    case BLANK:
                        xWinStreak = 0;
                        oWinStreak = 0;
                        break;
                }
                if(xWinStreak == winStreak) {
                    return Mark.X;
                } else if(oWinStreak == winStreak) {
                    return Mark.O;
                }
            }
        }
        return Mark.BLANK;
    }

    /*
     * Checks if there is a vertical win streak of one of the players. If so, returns true.
     * Otherwise, returns false
     */
    private Mark doesGameHaveVerticalWinStreak() {
        for(int col = 0; col < board.getSize(); col++) {
            int xWinStreak = 0;
            int oWinStreak = 0;
            for(int row = 0; row < board.getSize(); row++) {
                Mark mark = board.getMark(row, col);
                switch(mark) {
                    case X:
                        xWinStreak += 1;
                        oWinStreak = 0;
                        break;
                    case O:
                        oWinStreak += 1;
                        xWinStreak = 0;
                        break;
                    case BLANK:
                        xWinStreak = 0;
                        oWinStreak = 0;
                        break;
                }
                if(xWinStreak == winStreak) {
                    return Mark.X;
                } else if(oWinStreak == winStreak) {
                    return Mark.O;
                }
            }
        }
        return Mark.BLANK;
    }

    /*
     * Checks if there is a diagonal win streak (from top left to bottom right) of one of
     * the players. If so, returns true. Otherwise, returns false
     */
    private Mark doesGameHaveDiagonalFromTopLeftWinStreak() {
        for(int row = 0; row < board.getSize(); row++) {
            int xWinStreak = 0;
            int oWinStreak = 0;
            for(int delta = 0; delta < board.getSize() - row; delta++) {
                Mark mark = board.getMark(row + delta, delta);
                switch(mark) {
                    case X:
                        xWinStreak += 1;
                        oWinStreak = 0;
                        break;
                    case O:
                        oWinStreak += 1;
                        xWinStreak = 0;
                        break;
                    case BLANK:
                        xWinStreak = 0;
                        oWinStreak = 0;
                        break;
                }
                if(xWinStreak == winStreak) {
                    return Mark.X;
                } else if(oWinStreak == winStreak) {
                    return Mark.O;
                }
            }
        }
        return Mark.BLANK;
    }

    /*
     * Checks if there is a diagonal win streak (from top right to bottom left) of one of
     * the players. If so, returns true. Otherwise, returns false
     */
    private Mark doesGameHaveDiagonalFromTopRightWinStreak() {
        for(int row = 0; row < board.getSize(); row++) {
            int xWinStreak = 0;
            int oWinStreak = 0;
            for(int delta = 0; delta < board.getSize() - row; delta++) {
                Mark mark = board.getMark(row + delta, board.getSize() - 1 - delta);
                switch(mark) {
                    case X:
                        xWinStreak += 1;
                        oWinStreak = 0;
                        break;
                    case O:
                        oWinStreak += 1;
                        xWinStreak = 0;
                        break;
                    case BLANK:
                        xWinStreak = 0;
                        oWinStreak = 0;
                        break;
                }
                if(xWinStreak == winStreak) {
                    return Mark.X;
                } else if(oWinStreak == winStreak) {
                    return Mark.O;
                }
            }
        }
        return Mark.BLANK;
    }


}
