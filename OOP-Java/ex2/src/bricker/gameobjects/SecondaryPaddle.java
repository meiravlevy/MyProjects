package bricker.gameobjects;

import bricker.main.Constants;
import danogl.GameObject;
import danogl.collisions.Collision;
import danogl.util.Counter;

/**
 * secondary paddle of the game. Used when there is a main paddle in the game.
 * @author Meirav Levy
 */
public class SecondaryPaddle extends GameObject {
    private final GameObject objToFollow;
    private final Counter ballCollisionCounter;

    /**
     * Constructor.
     * @param objToFollow the object for the paddle to follow.
     * @param ballCollisionCounter a counter for the collisions of the secondary paddle with balls.
     */
    public SecondaryPaddle(GameObject objToFollow, Counter ballCollisionCounter) {
        super(objToFollow.getTopLeftCorner(), objToFollow.getDimensions(),
                objToFollow.renderer().getRenderable());
        this.objToFollow = objToFollow;
        this.ballCollisionCounter = ballCollisionCounter;
    }

    /**
     * Updates the secondary paddle. Includes updating the velocity.
     * Should be called once per frame.
     * @param deltaTime The time elapsed, in seconds, since the last frame. Can
     *                  be used to determine a new position/velocity by multiplying
     *                  this delta with the velocity/acceleration respectively
     *                  and adding to the position/velocity:
     *                  velocity += deltaTime*acceleration
     *                  pos += deltaTime*velocity
     */
    @Override
    public void update(float deltaTime) {
        super.update(deltaTime);
        setVelocity(objToFollow.getVelocity());
    }

    /**
     * Handles the secondary paddle on the first frame of a collision with other game object.
     * @param other The GameObject with which a collision occurred.
     * @param collision Information regarding this collision.
     *                  A reasonable elastic behavior can be achieved with:
     *                  setVelocity(getVelocity().flipped(collision.getNormal()));
     */
    @Override
    public void onCollisionEnter(GameObject other, Collision collision) {
        super.onCollisionEnter(other, collision);
        if(other.getTag().equals(Constants.MAIN_BALL_TAG) || other.getTag().equals(Constants.PUCK_TAG))
            ballCollisionCounter.increment();

    }
}