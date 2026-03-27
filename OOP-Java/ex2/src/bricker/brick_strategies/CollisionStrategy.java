package bricker.brick_strategies;

import danogl.GameObject;

/**
 * An interface describing the strategy of a game object once a collision occurs.
 */
public interface CollisionStrategy {
    /**
     * Performs the strategy when a collision occurs.
     * @param thisObj the current game object.
     * @param otherObj the game object that the current object is colliding with.
     */
    void onCollision(GameObject thisObj, GameObject otherObj);
}
