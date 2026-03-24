package bricker.main;

/**
 * Class for constants of the bricker game.
 */
public class Constants {

    /**
     * Constructor.
     */
    private Constants(){}

    /**
     * Tag of the main ball of the game.
     */
    public static final String MAIN_BALL_TAG = "main ball";

    /**
     * Tag of pucks of the game.
     */
    public static final String PUCK_TAG = "puck";

    /**
     * Tag of secondary paddle of the game.
     */
    public static final String SECONDARY_PADDLE_TAG = "secondary paddle";

    /**
     * Tag of main paddle of the game.
     */
    public static final String MAIN_PADDLE_TAG = "main paddle";

    /**
     * Tag of falling life in the game.
     */
    public static final String FALLING_LIFE_TAG = "falling life";

    /**
     * Tag of regular life displayed in the game.
     */
    public static final String REGULAR_LIFE_TAG = "life";

    /**
     * Heart image path.
     */
    public static final String HEART_IMAGE_PATH = "assets/heart.png";

    /**
     *
     */
    public static final String PUCK_IMAGE_PATH = "assets/mockBall.png";

    /**
     * Life game object image width.
     */
    public static final int LIFE_WIDTH = 15;

    /**
     * Maximum number of lives allowed in the game.
     */
    public static final int MAX_NUM_OF_LIVES = 4;

    /**
     * Paddle movement speed.
     */
    public static final float PADDLE_MOVEMENT_SPEED = 400;

    /**
     * Space between life objects of the graphical display.
     */
    public final static int SPACE_BETWEEN_LIVES = 2;

    /**
     * Speed of life when it falls down from a brick.
     */
    public static final int LIFE_SPEED = 100;

    /**
     * Puck speed.
     */
    public static final int PUCK_SPEED = 175;

    /**
     * The proportion of puck size to main ball size.
     */
    public static final float PUCK_PROPORTION_TO_BALL_SIZE = 0.75f;

    /**
     * number of pucks to create for MoreBallsStrategy
     */
    public static final int NUM_OF_PUCKS_TO_CREATE = 2;


    static final String WIN_ROUND_MESSAGE = "You win! Play again?";
    static final String LOSS_ROUND_MESSAGE = "You lose! Play again?";
    static final int PADDLE_WIDTH = 100;
    static final int BORDER_THICKNESS = 10;
    static final int PADDLE_HEIGHT = 15;
    static final int BALL_RADIUS = 20;
    static final int BALL_SPEED = 175;
    static final int DEFAULT_NUM_ROWS = 7;
    static final int DEFAULT_NUM_OF_BRICKS_IN_ROW = 8;
    static final int SPACE_BETWEEN_BRICKS = 5;
    static final int DEFAULT_NUM_OF_LIVES = 3;
    static final int BRICK_HEIGHT = 15;
    static final int NUM_OF_BALL_COLLISIONS_FOR_SETTING_CAMERA = 4;
    static final int MAX_NUM_SECONDARY_PADDLE_BALL_COLLISION = 4;
    static final int NUMERICAL_RENDERER_WIDTH = 15;
    static final int NUMERICAL_RENDERER_X_TOP_CORNER = 2;
    static final String BACKGROUND_IMAGE_PATH = "assets/DARK_BG2_small.jpeg";
    static final String BRICK_IMAGE_PATH = "assets/brick.png";
    static final String MAIN_BALL_IMAGE_PATH = "assets/ball.png";
    static final String BALL_COLLISION_SOUND_PATH = "assets/blop_cut_silenced.wav";
    static final String PADDLE_IMAGE_PATH = "assets/paddle.png";

}
