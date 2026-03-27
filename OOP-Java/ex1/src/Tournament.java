import java.awt.*;

/**
 * This class is intended to run a few rounds of a game between players.
 * @author Meirav Levy
 */
class Tournament {
    /**
     * The format in which the results are rendered to the screen.
     */
    public static final String PRINT_RESULT_FORMAT = "######### Results #########";

    private int rounds;
    private Renderer renderer;
    private Player player1;
    private Player player2;
    private int pointsPlayer1 = 0;
    private int pointsPlayer2 = 0;
    private int pointsTies = 0;

    /**
     * Constructor.
     * @param rounds the number of rounds of the game to pley.
     * @param renderer the renderer of the board.
     * @param player1 The first player of the tournament.
     * @param player2 the second player of the tournament.
     */
    public Tournament(int rounds, Renderer renderer, Player player1,
                      Player player2) {
        this.rounds = rounds;
        this.renderer = renderer;
        this.player1 = player1;
        this.player2 = player2;
    }

    /**
     * Runs a tournament of the game and in every round a different player goes first.
     * @param size the size of the board.
     * @param winStreak the streak of same mark needed to win a game.
     * @param playerName1 the name of the first player.
     * @param playerName2 the name of the second player.
     */
    public void playTournament(int size, int winStreak, String playerName1,
                               String playerName2) {
        for (int i = 0; i < rounds; i++) {
            if (i % 2 == 0) {
                Game game = new Game(player1, player2, size, winStreak, renderer);
                Mark gameResult1 = game.run();
                if (gameResult1 == Mark.X) {
                    pointsPlayer1 += 1;
                } else if (gameResult1 == Mark.O) {
                    pointsPlayer2 += 1;
                } else {
                    pointsTies += 1;
                }

            } else {
                Game game = new Game(player2, player1, size, winStreak, renderer);
                Mark gameResult2 = game.run();
                if (gameResult2 == Mark.X) {
                    pointsPlayer2 += 1;
                } else if (gameResult2 == Mark.O) {
                    pointsPlayer1 += 1;
                } else {
                    pointsTies += 1;
                }
            }
        }
        printResults(playerName1.toLowerCase(), playerName2.toLowerCase());
    }

    public static void main(String[] args) {
        int rounds = Integer.parseInt(args[0]);
        int boardSize = Integer.parseInt(args[1]);
        int winStreak = Integer.parseInt(args[2]);


        RendererFactory rendererFactory = new RendererFactory();
        Renderer renderer = rendererFactory.buildRenderer(args[3].toLowerCase(),
                Integer.parseInt(args[1]));
        if(renderer == null) {
            System.out.println(Constants.UNKNOWN_RENDERER_NAME);
            return;
        }
        PlayerFactory playerFactory = new PlayerFactory();
        Player player1 = playerFactory.buildPlayer(args[4].toLowerCase());
        if(player1 == null) {
            System.out.println(Constants.UNKNOWN_PLAYER_NAME);
            return;
        }
        Player player2 = playerFactory.buildPlayer(args[5].toLowerCase());
        if(player2 == null) {
            System.out.println(Constants.UNKNOWN_PLAYER_NAME);
            return;
        }
        Tournament tournament = new Tournament(rounds, renderer, player1, player2);
        tournament.playTournament(boardSize, winStreak, args[4], args[5]);
    }

    /*
    * Prints the results of a tournament between players.
    */
    private void printResults(String playerType1, String playerType2) {
        System.out.println(PRINT_RESULT_FORMAT);
        System.out.println(String.format("Player 1, %s won: %d rounds", playerType1,
                pointsPlayer1));
        System.out.println(String.format("Player 2, %s won: %d rounds", playerType2,
                pointsPlayer2));
        System.out.println(String.format("Ties: %d", pointsTies));
    }

}
