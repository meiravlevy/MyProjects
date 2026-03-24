package bricker.gameobjects;

import bricker.main.BrickerGameManager;
import bricker.main.Constants;
import danogl.GameObject;
import danogl.collisions.Collision;
import danogl.gui.rendering.Renderable;
import danogl.util.Counter;
import danogl.util.Vector2;

/**
 * A life game object that falls down.
 * @author Meirav Levy
 */
public class FallingLife extends GameObject {

    private final Counter curNumOfLivesInGame;
    private final BrickerGameManager brickerGameManager;

    /**
     * Construct a new GameObject instance.
     *
     * @param topLeftCorner Position of the object, in window coordinates (pixels).
     *                      Note that (0,0) is the top-left corner of the window.
     * @param dimensions    Width and height in window coordinates.
     * @param renderable    The renderable representing the object. Can be null, in which case
     *                      the GameObject will not be rendered.
     * @param curNumOfLivesInGame current num of lives in the game.
     * @param brickerGameManager bricker game manager.
     */
    public FallingLife(Vector2 topLeftCorner, Vector2 dimensions, Renderable renderable,
                       Counter curNumOfLivesInGame, BrickerGameManager brickerGameManager) {
        super(topLeftCorner, dimensions, renderable);
        this.curNumOfLivesInGame = curNumOfLivesInGame;
        this.brickerGameManager = brickerGameManager;
    }

    /**
     * Handles life game object on the first frame of a collision.
     * @param other The GameObject with which a collision occurred.
     * @param collision Information regarding this collision.
     *                  A reasonable elastic behavior can be achieved with:
     *                  setVelocity(getVelocity().flipped(collision.getNormal()));
     */
    @Override
    public void onCollisionEnter(GameObject other, Collision collision) {
        super.onCollisionEnter(other, collision);
        curNumOfLivesInGame.increment();
        brickerGameManager.removeGameObject(this);
    }

    /**
     * Should life game object be allowed to collide the specified other object. If both this object returns
     * true for the other, and the other returns true for this one, the collisions may occur when they
     * overlap, meaning that their respective onCollisionEnter/onCollisionStay/onCollisionExit will be called.
     * Note that this assumes that both objects have been added to the same
     * @param other The other GameObject.
     * @return true if the objects should collide. This does not guarantee a collision would actually
     * collide if they overlap, since the other object has to confirm this one as well.
     */
    @Override
    public boolean shouldCollideWith(GameObject other) {
        return other.getTag().equals(Constants.MAIN_PADDLE_TAG);
    }
}
