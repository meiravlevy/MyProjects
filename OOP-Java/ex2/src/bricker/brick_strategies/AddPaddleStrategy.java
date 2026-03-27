package bricker.brick_strategies;

import bricker.gameobjects.SecondaryPaddle;
import bricker.main.BrickerGameManager;
import bricker.main.Constants;
import danogl.GameObject;
import danogl.util.Counter;
import danogl.util.Vector2;

/**
 * Strategy that adds a paddle when collision occurs.
 */
public class AddPaddleStrategy implements CollisionStrategy {
    private final GameObject paddle;
    private final Vector2 windowDimensions;
    private final BrickerGameManager brickerGameManager;
    private final Counter numOfCurBricks;
    private final Counter ballCollisionCounter;

    /**
     * Constructor.
     * @param paddle paddle game object to add.
     * @param windowDimensions window dimensions of the game.
     * @param ballCollisionCounter counter of ball collisions with secondary paddle in the game.
     * @param brickerGameManager bricker game manager.
     * @param numOfCurBricks current number of bricks.
     */
    public AddPaddleStrategy(GameObject paddle,
                             Vector2 windowDimensions, Counter ballCollisionCounter,
                             BrickerGameManager brickerGameManager, Counter numOfCurBricks) {
        this.paddle = paddle;
        this.windowDimensions = windowDimensions;
        this.ballCollisionCounter = ballCollisionCounter;
        this.brickerGameManager = brickerGameManager;
        this.numOfCurBricks = numOfCurBricks;
    }

    /**
     * On collision, the current game object is removed and paddle game object is added instead (the paddle
     * is added only if there isn't a secondary paddle in the game already).
     * @param thisObj the current game object.
     * @param otherObj the game object that the current object is colliding with.
     */
    @Override
    public void onCollision(GameObject thisObj, GameObject otherObj) {
        if(!brickerGameManager.isSecondaryPaddleInGame()) {
            GameObject secondaryPaddle = new SecondaryPaddle(paddle, ballCollisionCounter);
            secondaryPaddle.setTag(Constants.SECONDARY_PADDLE_TAG);
            secondaryPaddle.setCenter(windowDimensions.mult(0.5f));
            brickerGameManager.addGameObject(secondaryPaddle);
        }
        if(brickerGameManager.removeGameObject(thisObj))
            numOfCurBricks.decrement();
    }
}