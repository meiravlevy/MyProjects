package bricker.brick_strategies;

import bricker.gameobjects.FallingLife;
import bricker.main.BrickerGameManager;
import bricker.main.Constants;
import danogl.GameObject;
import danogl.gui.ImageReader;
import danogl.util.Counter;
import danogl.util.Vector2;

/**
 * Strategy that adds a life when collision occurs with current object.
 */
public class AddLifeStrategy implements CollisionStrategy {
    private final ImageReader imageReader;
    private final Counter curNumOfLivesInGame;
    private final BrickerGameManager brickerGameManager;
    private final Counter numOfCurBricks;

    /**
     * Constructor.
     * @param imageReader renderable for printing images.
     * @param curNumOfLivesInGame current number of lives in the game.
     * @param brickerGameManager the bricker game manager.
     * @param numOfCurBricks current number of bricks in the game.
     */
    public AddLifeStrategy(ImageReader imageReader,
                           Counter curNumOfLivesInGame, BrickerGameManager brickerGameManager,
                           Counter numOfCurBricks) {
        this.imageReader = imageReader;
        this.curNumOfLivesInGame = curNumOfLivesInGame;
        this.brickerGameManager = brickerGameManager;
        this.numOfCurBricks = numOfCurBricks;
    }

    /**
     * On collision, the current game object is removed and life game object is added instead of it.
     * @param thisObj the current game object.
     * @param otherObj the game object that the current object is colliding with.
     */
    @Override
    public void onCollision(GameObject thisObj, GameObject otherObj) {
        GameObject life = new FallingLife(Vector2.ZERO, Vector2.ONES.mult(Constants.LIFE_WIDTH),
                imageReader.readImage(Constants.HEART_IMAGE_PATH, true),
                curNumOfLivesInGame, brickerGameManager);
        life.setTag(Constants.FALLING_LIFE_TAG);
        life.setCenter(thisObj.getTopLeftCorner().add(thisObj.getDimensions().mult(0.5f)));
        brickerGameManager.addGameObject(life);
        life.setVelocity(Vector2.DOWN.mult(Constants.LIFE_SPEED));
        if(brickerGameManager.removeGameObject(thisObj))
            numOfCurBricks.decrement();
    }
}
