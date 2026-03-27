package bricker.gameobjects;

import bricker.main.Constants;
import danogl.GameObject;
import danogl.gui.UserInputListener;
import danogl.gui.rendering.Renderable;
import danogl.util.Vector2;

import java.awt.event.KeyEvent;

/**
 * A paddle game object.
 * @author Meirav Levy
 */
public class Paddle extends GameObject {
    private final UserInputListener inputListener;

    /**
     * Construct a new GameObject instance.
     * @param topLeftCorner Position of the object, in window coordinates (pixels).
     *                      Note that (0,0) is the top-left corner of the window.
     * @param dimensions    Width and height in window coordinates.
     * @param renderable    The renderable representing the object. Can be null, in which case
     *                      the GameObject will not be rendered.
     * @param inputListener listens to keyboard input.
     */
    public Paddle(Vector2 topLeftCorner, Vector2 dimensions, Renderable renderable,
                  UserInputListener inputListener) {
        super(topLeftCorner, dimensions, renderable);
        this.inputListener = inputListener;
    }

    /**
     * Updates paddle's movement.
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
        Vector2 movementDir = Vector2.ZERO;
        if(inputListener.isKeyPressed(KeyEvent.VK_LEFT)){
            movementDir = movementDir.add(Vector2.LEFT.mult(Constants.PADDLE_MOVEMENT_SPEED));
        }
        if(inputListener.isKeyPressed(KeyEvent.VK_RIGHT)){
            movementDir = movementDir.add(Vector2.RIGHT.mult(Constants.PADDLE_MOVEMENT_SPEED));
        }
        setVelocity(movementDir);
    }
}
