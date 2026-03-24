package bricker.brick_strategies;

import bricker.main.BrickerGameManager;
import danogl.GameObject;
import danogl.gui.ImageReader;
import danogl.gui.Sound;
import danogl.util.Counter;
import danogl.util.Vector2;

import java.util.Random;

/**
 * A factory that builds brick strategies.
 */
public class BrickStrategyFactory {
    private static final int NUM_OF_SPECIAL_STRATEGIES = 2;
    private final Random rand = new Random();

    /**
     * Constructor.
     */
    public BrickStrategyFactory() {}

    /**
     *
     * @param brickerGameManager bricker game manager.
     * @param numOfCurBricks current number of bricks in the game.
     * @param ball the main ball of the game.
     * @param imageReader renderable for reading images.
     * @param ballCollisionSound sound of a ball when collision occurs.
     * @param paddle the main paddle of the game.
     * @param windowDimensions window dimensions of the game.
     * @param secondPaddleBallCollisionCounter counter of collisions between main ball and secondary paddle.
     * @param curNumOfLivesInGame number of current lives in the game.
     * @param numSelectedForStrategy selected number that strategies are picked according to.
     * @return collision strategy picked.
     */
    public CollisionStrategy buildStrategy(BrickerGameManager brickerGameManager,
                                           Counter numOfCurBricks, GameObject ball, ImageReader imageReader,
                                           Sound ballCollisionSound,
                                           GameObject paddle, Vector2 windowDimensions,
                                           Counter secondPaddleBallCollisionCounter,
                                           Counter curNumOfLivesInGame, int numSelectedForStrategy) {

        CollisionStrategy collisionStrategy;
        if (numSelectedForStrategy > 49)
            collisionStrategy = new BasicCollisionStrategy(brickerGameManager, numOfCurBricks);
        else {
            Counter curNumOfDoubleStrategies = new Counter();
            collisionStrategy = pickSpecialStrategy(brickerGameManager, numOfCurBricks, ball,
                    imageReader, ballCollisionSound,
                    paddle, windowDimensions, secondPaddleBallCollisionCounter,
                    curNumOfLivesInGame, numSelectedForStrategy, curNumOfDoubleStrategies);
        }

        return collisionStrategy;
    }


    /*
     * Picks special strategy.
     */
    private CollisionStrategy pickSpecialStrategy(BrickerGameManager brickerGameManager,
                                                  Counter numOfCurBricks, GameObject ball,
                                                  ImageReader imageReader,
                                                  Sound ballCollisionSound,
                                                  GameObject paddle, Vector2 windowDimensions,
                                                  Counter secondaryPaddleBallCollisionCounter,
                                                  Counter curNumOfLivesInGame,
                                                  int numSelectedForSpecialStrategy,
                                                  Counter numOfDoubleStrategies) {
        if (numSelectedForSpecialStrategy < 10)
            return new MoreBallsStrategy(ball, imageReader, ballCollisionSound,
                    brickerGameManager, numOfCurBricks);
        if (numSelectedForSpecialStrategy < 20)
            return new AddPaddleStrategy(paddle, windowDimensions,secondaryPaddleBallCollisionCounter,
                    brickerGameManager, numOfCurBricks);
        if (numSelectedForSpecialStrategy < 30)
            return new ChangeCameraStrategy(ball, windowDimensions, brickerGameManager, numOfCurBricks);
        if (numSelectedForSpecialStrategy < 40)
            return new AddLifeStrategy(imageReader, curNumOfLivesInGame, brickerGameManager, numOfCurBricks);

        return handleDoubleStrategy(brickerGameManager, numOfCurBricks, ball, imageReader,
                ballCollisionSound, paddle, windowDimensions, secondaryPaddleBallCollisionCounter,
                curNumOfLivesInGame, numOfDoubleStrategies);
    }


    /*
     * Handle situations where double strategy is picked. makes sure that there isn't more than one inner
     * double strategy.
     */
    private CollisionStrategy handleDoubleStrategy(BrickerGameManager brickerGameManager,
                                                   Counter numOfCurBricks, GameObject ball,
                                                   ImageReader imageReader, Sound ballCollisionSound,
                                                   GameObject paddle, Vector2 windowDimensions,
                                                   Counter paddleBallCollisionCounter,
                                                   Counter curNumOfLivesInGame,
                                                   Counter numOfDoubleStrategies) {
        int numSelectedForSpecialStrategy;
        if (numOfDoubleStrategies.value() == 2) {
            numSelectedForSpecialStrategy = rand.nextInt(40);
            return pickSpecialStrategy(brickerGameManager, numOfCurBricks, ball, imageReader,
                    ballCollisionSound, paddle, windowDimensions, paddleBallCollisionCounter,
                    curNumOfLivesInGame, numSelectedForSpecialStrategy, numOfDoubleStrategies);
        }
        return buildDoubleStrategy(brickerGameManager, numOfCurBricks, ball,
                imageReader, ballCollisionSound,
                paddle, windowDimensions, paddleBallCollisionCounter,
                curNumOfLivesInGame, numOfDoubleStrategies);
    }

    /*
     * Build a double strategy.
     */
    private CollisionStrategy buildDoubleStrategy(BrickerGameManager brickerGameManager,
                                                  Counter numOfCurBricks, GameObject ball,
                                                  ImageReader imageReader, Sound ballCollisionSound,
                                                  GameObject paddle, Vector2 windowDimensions,
                                                  Counter paddleBallCollisionCounter,
                                                  Counter curNumOfLivesInGame,
                                                  Counter numOfDoubleStrategies) {
        int numSelectedForSpecialStrategy;
        numOfDoubleStrategies.increment();
        CollisionStrategy[] collisionStrategies = new CollisionStrategy[NUM_OF_SPECIAL_STRATEGIES];
        for (int i = 0; i < NUM_OF_SPECIAL_STRATEGIES; i++) {
            numSelectedForSpecialStrategy = rand.nextInt(50);
            collisionStrategies[i] = pickSpecialStrategy(brickerGameManager, numOfCurBricks, ball,
                    imageReader, ballCollisionSound,
                    paddle, windowDimensions, paddleBallCollisionCounter,
                    curNumOfLivesInGame, numSelectedForSpecialStrategy, numOfDoubleStrategies);
        }
        return new DoubleStrategy(collisionStrategies, brickerGameManager, numOfCurBricks);

    }

}