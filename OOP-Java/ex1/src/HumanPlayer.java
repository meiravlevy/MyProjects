/**
 * A human player of a game. It is used when it's the human player's turn in
 * the game.
 * @author Meirav Levy
 */
class HumanPlayer implements Player{

    /**
     * constructor.
     */
    public HumanPlayer() {}

    /**
     * Plays a turn of the human player in the game.
     * @param board the board of the game.
     * @param mark the mark symbol of the human player.
     */
    public void playTurn(Board board, Mark mark) {
        System.out.println(Constants.playerRequestInputString(mark.toString()));
        int positionInBoard = KeyboardInput.readInt();
        int row = positionInBoard / 10;
        int col = positionInBoard % 10;
        while(!board.putMark(mark, row, col)) {
            notify_user_of_invalid_mark(board, row, col);
            positionInBoard = KeyboardInput.readInt();
            row = positionInBoard / 10;
            col = positionInBoard % 10;
        }
    }

    /*
    * Notifies the user why he couldn't put his mark on the board.
    */
    private void notify_user_of_invalid_mark(Board board, int row, int col) {
        if(board.getMark(row, col) == Mark.BLANK) {
            System.out.println(Constants.INVALID_COORDINATE);
        } else {
            System.out.println(Constants.OCCUPIED_COORDINATE);
        }
    }

}
