package bricker.brick_strategies;

import bricker.main.BrickerGameManager;
import danogl.GameObject;
import danogl.util.Counter;

/**
 * Strategy that adds two special strategies when collision occurs.
 */
public class DoubleStrategy implements CollisionStrategy{
    CollisionStrategy[] collisionStrategies;
    private final BrickerGameManager brickerGameManager;
    private final Counter numOfCurBricks;

    /**
     * Constructor.
     * @param collisionStrategies an array of collision strategies.
     * @param brickerGameManager bricker game manager.
     * @param numOfCurBricks current number of bricks in game.
     */
    public DoubleStrategy(CollisionStrategy[] collisionStrategies,
                          BrickerGameManager brickerGameManager, Counter numOfCurBricks) {
        this.collisionStrategies = new CollisionStrategy[collisionStrategies.length];
        for (int i = 0; i < collisionStrategies.length; i++) {
            this.collisionStrategies[i] = collisionStrategies[i];
        }
        this.brickerGameManager = brickerGameManager;
        this.numOfCurBricks = numOfCurBricks;
    }

    /**
     * On collision, current object is removed and two strategies are activated.
     * @param thisObj the current game object.
     * @param otherObj the game object that the current object is colliding with.
     */
    @Override
    public void onCollision(GameObject thisObj, GameObject otherObj) {
        for (CollisionStrategy collisionStrategy : collisionStrategies) {
            if (collisionStrategy != null)
                collisionStrategy.onCollision(thisObj, otherObj);
        }
        if(brickerGameManager.removeGameObject(thisObj))
            numOfCurBricks.decrement();
    }
}
