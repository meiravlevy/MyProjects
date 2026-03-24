/**
 * Represents a board game. This board is intended for use in a game.
 * @author Meirav Levy
 */
class Board {
    /**
     * The default size of the board if size not given.
     */
    public static final int DEFAULT_SIZE_OF_BOARD = 4;
    /**
     * The index of the first row on the board.
     */
    public static final int FIRST_ROW_INDEX = 0;
    /**
     * The index of the first column on the board.
     */
    public static final int FIRST_COL_INDEX = 0;

    private Mark[][] board;

    /**
     * constructor. initializes an empty board with default size.
     */
    public Board() {
        this.board = new Mark[DEFAULT_SIZE_OF_BOARD][DEFAULT_SIZE_OF_BOARD];
        this.fill_board_with_blanks();
    }

    /**
     * Constructor.
     * @param size size of the board.
     */
    public Board(int size) {
        this.board = new Mark[size][size];
        this.fill_board_with_blanks();
    }

    /**
     * Returns the size of the current board.
     * @return size of current board(length of row).
     */
    public int getSize() {
        return board.length;
    }

    /**
     * Puts a mark on the board. If the spot on the board is already occupied,
     * the method will have no effect.
     * @param mark the mark representing the player.
     * @param row the row to put the mark in.
     * @param col the column to put the mark in.
     * @return true if the mark was successfully put on the board. False otherwise.
     */
    public boolean putMark(Mark mark, int row, int col) {
        if(row < 0 || row >= board.length  || col < 0 ||
                col >= board.length || board[row][col] != Mark.BLANK) {
            return false;
        }
        board[row][col] = mark;
        return true;
    }

    /**
     * Returns the mark in the specified coordinates on the board .
     * @param row row coordinate.
     * @param col column coordinate.
     * @return mark if the specified coordinates are legal. Otherwise,
     * returns blank.
     */
    public Mark getMark(int row, int col) {
        if(row < 0 || row >= board.length || col < 0 || col >= board.length) {
            return Mark.BLANK;
        }
        return board[row][col];
    }

    /*
    * Fills board with blanks.
    */
    private void fill_board_with_blanks() {
        for(int row = 0; row < board.length; row++) {
            for(int col = 0; col < board[row].length; col++) {
                board[row][col] = Mark.BLANK;
            }
        }
    }

}
