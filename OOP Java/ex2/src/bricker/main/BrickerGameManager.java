package bricker.main;

import bricker.brick_strategies.BrickStrategyFactory;
import bricker.brick_strategies.CollisionStrategy;
import bricker.gameobjects.*;
import danogl.GameManager;
import danogl.GameObject;
import danogl.collisions.Layer;
import danogl.components.CoordinateSpace;
import danogl.gui.*;
import danogl.gui.rendering.Renderable;
import danogl.gui.rendering.TextRenderable;
import danogl.util.Counter;
import danogl.util.Vector2;

import java.awt.event.KeyEvent;
import java.util.Random;

/**
 * This class is intended to run the bricker game.
 * @author Meirav Levy
 */
public class BrickerGameManager extends GameManager{

    private final Random rand = new Random();
    private final Counter secondPaddleBallCollisionsCounter = new Counter();
    private final int numRows;
    private final int numOfBricksInRow;
    private Counter curNumOfLives;
    private Counter curNumOfBricks;
    private GameObject leftBorder;
    private GameObject rightBorder;
    private Ball ball;
    private int ballCollisions = 0;
    private GameObject paddle;
    private Vector2 windowDimensions;
    private WindowController windowController;
    private UserInputListener inputListener;
    private ImageReader imageReader;
    private Sound ballCollisionSound;

    /**
     * Constructor.
     * @param windowTitle title for the window of the game.
     * @param windowDimensions window dimensions.
     */
    public BrickerGameManager(String windowTitle, Vector2 windowDimensions) {
        super(windowTitle, windowDimensions);
        this.numRows = Constants.DEFAULT_NUM_ROWS;
        this.numOfBricksInRow = Constants.DEFAULT_NUM_OF_BRICKS_IN_ROW;
    }

    /**
     * Constructor.
     * @param windowTitle title for the window of the game.
     * @param windowDimensions window dimensions.
     * @param numOfBricksInRow number of bricks in a row.
     * @param numRows num of rows of bricks.
     */
    public BrickerGameManager(String windowTitle, Vector2 windowDimensions,
                              int numOfBricksInRow, int numRows) {
        super(windowTitle, windowDimensions);
        this.numOfBricksInRow = numOfBricksInRow;
        this.numRows = numRows;
    }

    /**
     * Initializes a bricker game.
     * @param imageReader Contains a single method: readImage, which reads an image from disk.
     *                 See its documentation for help.
     * @param soundReader Contains a single method: readSound, which reads a wav file from
     *                    disk. See its documentation for help.
     * @param inputListener Contains a single method: isKeyPressed, which returns whether
     *                      a given key is currently pressed by the user or not. See its
     *                      documentation.
     * @param windowController Contains an array of helpful, self explanatory methods
     *                         concerning the window.
     */
    @Override
    public void initializeGame(ImageReader imageReader, SoundReader soundReader,
                               UserInputListener inputListener, WindowController windowController) {
        super.initializeGame(imageReader, soundReader, inputListener, windowController);
        this.windowController = windowController;
        this.windowDimensions = windowController.getWindowDimensions();
        this.curNumOfLives = new Counter(Constants.DEFAULT_NUM_OF_LIVES);
        this.curNumOfBricks = new Counter(numRows * numOfBricksInRow);
        this.inputListener = inputListener;
        secondPaddleBallCollisionsCounter.reset();

        this.imageReader = imageReader;
        //create borders
        createBorders();

        //create ball
        createBall(soundReader);

        //create paddle
        createPaddle();

        //create background
        createBackground();

        //create bricks
        createBricks();

        //create numerical life renderer
        createNumericalLifeRenderer();

        //create graphic life renderer
        createGraphicLifeRenderer();
    }

    /**
     * Remove game object from game objects.
     * @param obj the object to remove
     * @return true if remove was successful. false otherwise.
     */
    public boolean removeGameObject(GameObject obj) {
        return gameObjects().removeGameObject(obj, Layer.STATIC_OBJECTS)
                || gameObjects().removeGameObject(obj)
                || gameObjects().removeGameObject(obj, Layer.UI)
                || gameObjects().removeGameObject(obj, Layer.BACKGROUND);
    }

    /**
     * Add game object to game object. Unless game object is falling life game object, then the game object
     * is added to the default layer.
     * @param obj game object ot add.
     */
    public void addGameObject(GameObject obj) {
        if(obj.getTag().equals(Constants.REGULAR_LIFE_TAG))
            gameObjects().addGameObject(obj, Layer.UI);
        else {
            gameObjects().addGameObject(obj);
        }
    }

    //todo: check if i should do an interface of exceeding borders of game objects or something like that.

    /**
     * updates different parts of the game.
     * @param deltaTime The time, in seconds, that passed since the last invocation
     *                  of this method (i.e., since the last frame). This is useful
     *                  for either accumulating the total time that passed since some
     *                  event, or for physics integration (i.e., multiply this by
     *                  the acceleration to get an estimate of the added velocity or
     *                  by the velocity to get an estimate of the difference in position).
     */
    @Override
    public void update(float deltaTime) {
        super.update(deltaTime);
        keepPaddlesInBorders();
        removeSecondaryPaddle();
        handlePucksAndLivesExceedBorders();
        updateCamera();
        updateLives();
        checkAndHandleEndOfRound();
    }

    /**
     * checks if there is currently a secondary paddle in the game.
     * @return true is there is. False otherwise.
     */
    public boolean isSecondaryPaddleInGame() {
        for(GameObject obj : gameObjects()) {
            if(obj.getTag().equals(Constants.SECONDARY_PADDLE_TAG))
                return true;
        }
        return false;
    }

    /**
     * returns the current number of lives in game.
     * @return current number of lives in game.
     */
    public int getNumOfLivesInGame() {return curNumOfLives.value();}

    /*
     * if current number of lives is bigger than the maximum number of lives allowed in game, decreases the
     *  number of lives.
     */
    private void updateLives() {
        while(curNumOfLives.value() > Constants.MAX_NUM_OF_LIVES) {
            curNumOfLives.decrement();
        }
    }

    /*
     * If camera is following ball, and ball has collided with game objects a fixed amount of times,
     * resets camera.
     */
    private void updateCamera() {
        if(camera() == null)
            ballCollisions = ball.getCollisionCounter();
        if(camera() != null &&
                ball.getCollisionCounter() >= ballCollisions +
                        Constants.NUM_OF_BALL_COLLISIONS_FOR_SETTING_CAMERA) {
            setCamera(null);
        }
    }

    /*
     * If secondary paddle currently in game and the number of collisions between main ball is equal to the
     * maximum number of collisions allowed between them, the secondary paddle is removed.
     */
    private void removeSecondaryPaddle() {
        for(GameObject obj : gameObjects()) {
            if(obj.getTag().equals(Constants.SECONDARY_PADDLE_TAG) &&
                    secondPaddleBallCollisionsCounter.value() ==
                            Constants.MAX_NUM_SECONDARY_PADDLE_BALL_COLLISION) {
                removeGameObject(obj);
                secondPaddleBallCollisionsCounter.reset();
            }
        }
    }

    /*
     * Make sure that paddles(main paddle and secondary paddle) don't exceed borders.
     */
    private void keepPaddlesInBorders() {
        for(GameObject obj : gameObjects()){
            if(obj == paddle || obj.getTag().equals(Constants.SECONDARY_PADDLE_TAG))
                keepPaddleInBorders(obj);
        }

    }

    /*
     * Make sure that paddle doesn't exceed borders.
     */
    private void keepPaddleInBorders(GameObject paddle) {
        if(paddle.getTopLeftCorner().x() < leftBorder.getDimensions().x()) {
            paddle.setTopLeftCorner(new Vector2(leftBorder.getDimensions().x(),
                    paddle.getTopLeftCorner().y()));
        }
        if(paddle.getTopLeftCorner().x() > rightBorder.getTopLeftCorner().x() - paddle.getDimensions().x()) {
            paddle.setTopLeftCorner(new Vector2(
                    rightBorder.getTopLeftCorner().x() - paddle.getDimensions().x(),
                    paddle.getTopLeftCorner().y()));
        }
    }

    /*
     * If puck or life exceeds borders, they are removed from the game objects.
     */
    private void handlePucksAndLivesExceedBorders() {
        for(GameObject obj: gameObjects()){
            if(obj.getTag().equals(Constants.PUCK_TAG) || obj.getTag().equals(Constants.FALLING_LIFE_TAG)) {
                float objHeight = obj.getCenter().y();
                if(objHeight > windowDimensions.y())
                    removeGameObject(obj);
            }
        }
    }

    /*
     * Handle end of round(either loss in the game or win).
     */
    private void checkAndHandleEndOfRound() {
        if(curNumOfBricks.value() == 0 || inputListener.isKeyPressed(KeyEvent.VK_W)) {
            handleWinOfRound();
        }
        float ballHeight = ball.getCenter().y();
        if(ballHeight > windowDimensions.y())
            handleRoundLoss();
    }

    /*
     * Handle win of the round.
     */
    private void handleWinOfRound() {
        String prompt  = Constants.WIN_ROUND_MESSAGE;
        checkIfPlayAgain(prompt);
    }

    /*
     * Handle loss of the round.
     */
    private void handleRoundLoss() {
        curNumOfLives.decrement();
        if (curNumOfLives.value() > 0) {
            ball.setCenter(windowDimensions.mult(0.5f));
            createRandomBallVelocity();
        } else {
            String prompt = Constants.LOSS_ROUND_MESSAGE;
            checkIfPlayAgain(prompt);
        }
    }

    /*
     * Asks the user if he would like to play another game, and behaves accordingly.
     */
    private void checkIfPlayAgain(String prompt) {
        if (windowController.openYesNoDialog(prompt))
            windowController.resetGame();
        else
            windowController.closeWindow();
    }

    /*
     * Creates a numerical renderer of current number of lives in the game.
     */
    private void createNumericalLifeRenderer() {
        TextRenderable textRenderable = new TextRenderable("");
        GameObject numericalLifeRenderer = new NumericalLifeRenderer(
                new Vector2(Constants.NUMERICAL_RENDERER_X_TOP_CORNER,
                        windowDimensions.y() - Constants.NUMERICAL_RENDERER_WIDTH - 3),
                Vector2.ONES.mult(Constants.NUMERICAL_RENDERER_WIDTH), textRenderable, this);
        gameObjects().addGameObject(numericalLifeRenderer, Layer.UI);
    }

    /*
     * Creates a graphical renderer of the current number of lives in the game.
     */
    private void createGraphicLifeRenderer() {
        Renderable heartImage =  imageReader.readImage(Constants.HEART_IMAGE_PATH,
                true);
        GameObject graphicRenderer = new GraphicLifeRenderer(new Vector2(
                Constants.NUMERICAL_RENDERER_X_TOP_CORNER + Constants.NUMERICAL_RENDERER_WIDTH,
                                windowDimensions.y() - Constants.NUMERICAL_RENDERER_WIDTH - 3),
                        Vector2.ONES.mult(Constants.LIFE_WIDTH), heartImage, this);
        gameObjects().addGameObject(graphicRenderer, Layer.UI);
    }

    /*
     * Creates the bricks of the game.
     */
    private void createBricks() {
        BrickStrategyFactory brickStrategyFactory = new BrickStrategyFactory();
        Renderable brickImage = imageReader.readImage(Constants.BRICK_IMAGE_PATH,
                false);
        float brickWidth = (windowDimensions.x()
                - (Constants.BORDER_THICKNESS * 2)
                - (Constants.SPACE_BETWEEN_BRICKS * (numOfBricksInRow - 1))) / numOfBricksInRow;
        float brickYStart = Constants.BORDER_THICKNESS;
        for (int i = 0; i < numRows; i++) {
            createRowOfBricks(brickStrategyFactory, brickImage, brickYStart, brickWidth);
            brickYStart += Constants.BRICK_HEIGHT + Constants.SPACE_BETWEEN_BRICKS;
        }
    }

    /*
     * Creates row of bricks.
     */
    private void createRowOfBricks(BrickStrategyFactory brickStrategyFactory, Renderable brickImage,
                                   float brickYStart,
                                   float brickWidth) {
        float brickXStart = Constants.BORDER_THICKNESS;
        for (int i = 0; i < numOfBricksInRow; i++) {
            createBrick(brickStrategyFactory, brickImage, brickXStart,brickYStart, brickWidth);
            brickXStart += brickWidth + Constants.SPACE_BETWEEN_BRICKS;
        }
    }

    /*
     * create one brick game object.
     */
    private void createBrick(BrickStrategyFactory brickStrategyFactory, Renderable brickImage,
                             float xStartOfBrick,
                             float brickYStart,
                             float brickWidth) {
        GameObject brick = new Brick(new Vector2(xStartOfBrick, brickYStart),
                new Vector2(brickWidth, Constants.BRICK_HEIGHT), brickImage,
                selectBrickStrategy(brickStrategyFactory));
        gameObjects().addGameObject(brick, Layer.STATIC_OBJECTS);
    }

    /*
     * Select a brick strategy.
     */
    private CollisionStrategy selectBrickStrategy(BrickStrategyFactory brickStrategyFactory) {
        int percentageForStrategy = rand.nextInt(100);
        return brickStrategyFactory.buildStrategy( this, curNumOfBricks,
                ball, imageReader, ballCollisionSound,
                paddle, windowDimensions, secondPaddleBallCollisionsCounter,
                curNumOfLives, percentageForStrategy);
    }

    /*
     * Create a background game object.
     */
    private void createBackground() {
        Renderable backgroundImage = imageReader.readImage(Constants.BACKGROUND_IMAGE_PATH,
                false);
        GameObject background = new GameObject(Vector2.ZERO, windowDimensions, backgroundImage);
        background.setCoordinateSpace(CoordinateSpace.CAMERA_COORDINATES);
        gameObjects().addGameObject(background, Layer.BACKGROUND);
    }

    /*
     * create borders game objects.
     */
    private void createBorders() {
        //create left wall
        leftBorder = createBorder(Vector2.ZERO,
                new Vector2(Constants.BORDER_THICKNESS, windowDimensions.y()));

        //create right wall
        rightBorder = createBorder(new Vector2(windowDimensions.x() - Constants.BORDER_THICKNESS, 0),
                new Vector2(Constants.BORDER_THICKNESS, windowDimensions.y()));

        //create upper wall
        createBorder(Vector2.ZERO, new Vector2(windowDimensions.x(), Constants.BORDER_THICKNESS));
    }

    /*
     * create one border game object.
     */
    private GameObject createBorder(Vector2 topLeftCorner, Vector2 size) {
        GameObject wall = new GameObject(topLeftCorner, size, null);
        gameObjects().addGameObject(wall, Layer.STATIC_OBJECTS);
        return wall;
    }

    /*
     * Create paddle game object.
     */
    private void createPaddle() {
        Renderable paddleImage = imageReader.readImage(Constants.PADDLE_IMAGE_PATH,
                true);
        paddle = new Paddle(Vector2.ZERO, new Vector2(Constants.PADDLE_WIDTH, Constants.PADDLE_HEIGHT),
                paddleImage,
                inputListener);
        paddle.setCenter(new Vector2(windowDimensions.x()/2, windowDimensions.y()-30));
        gameObjects().addGameObject(paddle);
        paddle.setTag(Constants.MAIN_PADDLE_TAG);
    }

    /*
     * Create ball game object.
     */
    private void createBall(SoundReader soundReader) {
        Renderable ballImage = imageReader.readImage(Constants.MAIN_BALL_IMAGE_PATH,
                true);
        ballCollisionSound = soundReader.readSound(Constants.BALL_COLLISION_SOUND_PATH);
        ball = new Ball(Vector2.ZERO, new Vector2(Constants.BALL_RADIUS, Constants.BALL_RADIUS),
                ballImage, ballCollisionSound);
        ball.setCenter(windowDimensions.mult(0.5f));
        gameObjects().addGameObject(ball);
        ball.setTag(Constants.MAIN_BALL_TAG);
        createRandomBallVelocity();

    }

    /*
     * Create random velocity for main ball of the game.
     */
    private void createRandomBallVelocity() {
        float ballVelX = Constants.BALL_SPEED;
        float ballVelY = Constants.BALL_SPEED;
        if(rand.nextBoolean())
            ballVelX *= -1;
        if(rand.nextBoolean())
            ballVelY *= -1;
        ball.setVelocity(new Vector2(ballVelX, ballVelY));
    }

    /**
     * Runs the bricker game.
     * @param args arguments from command line.
     */
    public static void main(String[] args) {
        if(args.length != 2) {
            new BrickerGameManager("Bricker",
                    new Vector2(700, 500)).run();
            return;
        }
        int numOfBricksInRow = Integer.parseInt(args[0]);
        int numRows = Integer.parseInt(args[1]);
        new BrickerGameManager("Bricker",
                new Vector2(700, 500), numOfBricksInRow, numRows).run();

    }
}
