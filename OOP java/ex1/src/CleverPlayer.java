/**
 * A clever player of a game. It is used when it's the clever player's turn in
 * the game. The clever player has a specific strategy that helps him win whatever
 * player in the majority of the games.
 * @author Meirav Levy
 * @see WhateverPlayer
 */
class CleverPlayer implements Player{

    private static final int STRATEGY_ROW = 0; // The player will try and create a win streak in this row.
    private Player whateverPlayer = new WhateverPlayer();


    /**
     * constructor.
     */
    public CleverPlayer() {}

    /**
     * Plays a turn of the clever player in the game.
     * @param board the board of the game.
     * @param mark the mark symbol of the clever player.
     */
    public void playTurn(Board board, Mark mark) {
        if(!putMarkInFirstAvailablePositionInStrategyRow(board, mark)) {
            whateverPlayer.playTurn(board, mark);
        }
    }

    /*
    * Tries to put a mark on the first available position in row 0 of the board.
    * Returns true if succeeds. Otherwise, false.
    */
    private boolean putMarkInFirstAvailablePositionInStrategyRow(Board board, Mark mark) {
        for(int col = 0; col < board.getSize(); col++) {
            if(board.getMark(STRATEGY_ROW, col) == Mark.BLANK) {
                return board.putMark(mark, STRATEGY_ROW, col);
            }
        }
        return false;
    }


}