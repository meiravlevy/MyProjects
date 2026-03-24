/**
 * A genius player of the game. It is used when it's the Genius turn in the game.
 * The genius player has a specific strategy that helps him win whatever and clever players
 * in the majority of the games.
 * @author Meirav Levy
 * @see WhateverPlayer
 * @see CleverPlayer
 */
class GeniusPlayer implements Player {

    private static final int STRATEGY_COL = 2; // The player will try and create a win streak in this column.
    private Player whateverPlayer = new WhateverPlayer();

    /**
     * constructor.
     */
    public GeniusPlayer() {}

    /**
     * Plays a turn of the Genius player in the game.
     * @param board the board of the game.
     * @param mark the mark symbol of the genius player.
     */
    public void playTurn(Board board, Mark mark) {
        if(!putMarkInFirstAvailablePositionInStrategyColumn(board, mark)) {
            whateverPlayer.playTurn(board, mark);
        }
    }

    /*
     * Tries to put a mark on the first available spot in the player's strategy column
     * of the board.
     * Returns true if succeeds. Otherwise, false.
     */
    private boolean putMarkInFirstAvailablePositionInStrategyColumn(Board board, Mark mark) {
        for(int row = 0; row < board.getSize(); row++) {
            if(board.getMark(row, STRATEGY_COL) == Mark.BLANK) {
                return board.putMark(mark, row, STRATEGY_COL);
            }
        }
        return false;
    }

}
