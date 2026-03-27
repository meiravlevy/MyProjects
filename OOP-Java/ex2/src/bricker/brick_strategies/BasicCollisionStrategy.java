package bricker.brick_strategies;

import bricker.main.BrickerGameManager;
import danogl.GameObject;
import danogl.util.Counter;

/**
 * Basic strategy that removes the current object when collision occurs.
 */
public class BasicCollisionStrategy implements CollisionStrategy{
    private final BrickerGameManager brickerGameManager;
    private final Counter numOfCurBricks;

    /**
     * Constructor.
     * @param brickerGameManager bricker game manager.
     * @param numOfCurBricks current number of bricks in the game.
     */
    public BasicCollisionStrategy(BrickerGameManager brickerGameManager, Counter numOfCurBricks) {
        this.brickerGameManager = brickerGameManager;
        this.numOfCurBricks = numOfCurBricks;
    }

    /**
     * On collision of current game object with other game object, current game object is removed.
     * @param thisObj the current game object.
     * @param otherObj the game object that the current object is colliding with.
     */
    @Override
    public void onCollision(GameObject thisObj, GameObject otherObj) {
        if(brickerGameManager.removeGameObject(thisObj))
            numOfCurBricks.decrement();
    }
}
