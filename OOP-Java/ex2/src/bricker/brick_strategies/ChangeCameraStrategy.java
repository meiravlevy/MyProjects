package bricker.brick_strategies;

import bricker.main.BrickerGameManager;
import bricker.main.Constants;
import danogl.GameObject;
import danogl.gui.rendering.Camera;
import danogl.util.Counter;
import danogl.util.Vector2;

/**
 * Strategy that changes the camera when collision occurs.
 */
public class ChangeCameraStrategy implements CollisionStrategy{
    private final GameObject objToFollow;
    private final Vector2 windowDimensions;
    private final BrickerGameManager brickerGameManager;
    private final Counter numOfCurBricks;

    /**
     * constructor.
     * @param objToFollow object for camera to follow.
     * @param windowDimensions window dimensions of the game.
     * @param brickerGameManager the bricker game manager.
     * @param numOfCurBricks current number of bricks in the game.
     */
    public ChangeCameraStrategy(GameObject objToFollow, Vector2 windowDimensions,
                                BrickerGameManager brickerGameManager, Counter numOfCurBricks) {
        this.objToFollow = objToFollow;
        this.windowDimensions = windowDimensions;
        this.brickerGameManager = brickerGameManager;
        this.numOfCurBricks = numOfCurBricks;
    }

    /**
     * On collision with main ball, this object is removed and camera is set to follow objToFollow(only if
     * camera isn't currently set already)
     * @param thisObj the current game object.
     * @param otherObj the game object that the current object is colliding with.
     */
    @Override
    public void onCollision(GameObject thisObj, GameObject otherObj) {
        if(brickerGameManager.camera() == null && otherObj.getTag().equals(Constants.MAIN_BALL_TAG)) {
            brickerGameManager.setCamera(new Camera(objToFollow, Vector2.ZERO,
                    windowDimensions.mult(1.2f), windowDimensions));
        }
        if(brickerGameManager.removeGameObject(thisObj))
            numOfCurBricks.decrement();
    }
}
