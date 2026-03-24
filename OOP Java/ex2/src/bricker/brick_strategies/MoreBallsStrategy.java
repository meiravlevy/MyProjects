package bricker.brick_strategies;

import bricker.gameobjects.Ball;
import bricker.main.BrickerGameManager;
import bricker.main.Constants;
import danogl.GameObject;
import danogl.gui.ImageReader;
import danogl.gui.Sound;
import danogl.gui.rendering.Renderable;
import danogl.util.Counter;
import danogl.util.Vector2;
import java.util.Random;


/**
 * Strategy that adds two pucks to the game when collision occurs.
 */
public class MoreBallsStrategy implements CollisionStrategy{

    private final GameObject origBall;
    private final ImageReader imageReader;
    private final Sound ballCollisionSound;
    private final BrickerGameManager brickerGameManager;
    private final Counter numOfCurBricks;

    private final Random random = new Random();

    /**
     * Constructor.
     * @param origBall original ball for creating the puck according to it.
     * @param imageReader renderable for reading images.
     * @param ballCollisionSound sound of ball when collision occurs.
     * @param brickerGameManager bricker game manager.
     * @param numOfCurBricks current number of cricks in game.
     */
    public MoreBallsStrategy(GameObject origBall, ImageReader imageReader, Sound ballCollisionSound,
                             BrickerGameManager brickerGameManager, Counter numOfCurBricks) {
        this.origBall = origBall;
        this.imageReader = imageReader;
        this.ballCollisionSound = ballCollisionSound;
        this.brickerGameManager = brickerGameManager;
        this.numOfCurBricks = numOfCurBricks;
    }

    /**
     * On collision, current object is removed and fixed amount of pucks are created instead.
     * @param thisObj the current game object.
     * @param otherObj the game object that the current object is colliding with.
     */
    @Override
    public void onCollision(GameObject thisObj, GameObject otherObj) {
        for (int i = 0; i < Constants.NUM_OF_PUCKS_TO_CREATE; i++) {
            GameObject puck = createPuck(thisObj);
            brickerGameManager.addGameObject(puck);
            createRandomPuckVelocity(puck);
        }
        if(brickerGameManager.removeGameObject(thisObj))
            numOfCurBricks.decrement();
    }

    /*
     * Creates one puck game object and sets it in the middle of the current object.
     * Returns the puck created.
     */
    private GameObject createPuck(GameObject thisObj) {
        Renderable puckImage = imageReader.readImage(Constants.PUCK_IMAGE_PATH, true);
        GameObject puck = new Ball(Vector2.ZERO,
                origBall.getDimensions().mult(Constants.PUCK_PROPORTION_TO_BALL_SIZE),
                puckImage, ballCollisionSound);
        puck.setCenter(thisObj.getTopLeftCorner().add(thisObj.getDimensions().mult(0.5f)));
        puck.setTag(Constants.PUCK_TAG);
        return puck;
    }

    /*
     * Create random velocity for puck.
     */
    private void createRandomPuckVelocity(GameObject puck) {
        double angle = random.nextDouble() * Math.PI;
        float velocityX = (float)Math.cos(angle) * Constants.PUCK_SPEED;
        float velocityY = (float)Math.sin(angle) * Constants.PUCK_SPEED;
        puck.setVelocity(new Vector2(velocityX, velocityY));
    }
}

