import java.util.Random;

/**
 * A player of the games that doesn't have a concrete strategy. It is used when it's
 * the whatever player's turn in the game.
 * @author Meirav Levy
 */
class WhateverPlayer implements Player{

    private Random rand = new Random();

    /**
     * Constructor.
     */
    public WhateverPlayer() {}

    /**
     * Plays a turn of the whatever player in the game.
     * @param board the board of the game.
     * @param mark the mark symbol of the whatever player.
     */
    public void playTurn(Board board, Mark mark) {
        int randomRow = rand.nextInt(board.getSize());
        int randomCol = rand.nextInt(board.getSize());
        while(!board.putMark(mark, randomRow, randomCol)) {
            randomRow = rand.nextInt(board.getSize());
            randomCol = rand.nextInt(board.getSize());
        }
    }
}
