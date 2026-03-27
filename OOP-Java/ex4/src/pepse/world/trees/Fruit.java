package pepse.world.trees;

import danogl.GameObject;
import danogl.collisions.Collision;
import danogl.components.ScheduledTask;
import danogl.gui.rendering.OvalRenderable;
import danogl.util.Vector2;
import pepse.Constants;
import pepse.world.Observer;
import java.awt.*;
import java.util.function.Consumer;

/**
 * A class representing a fruit game object in the game's world.
 * @author Meirav Levy
 */
public class Fruit extends GameObject implements Observer {
    private final Consumer<Double> onCollisionsOtherCallback;
    private Color fruitColor;

    /**
     * Construct a new GameObject instance.
     *
     * @param topLeftCorner Position of the object, in window coordinates (pixels).
     *                      Note that (0,0) is the top-left corner of the window.
     * @param dimensions    Width and height in window coordinates.
     * @param onCollisionsOtherCallback Callback function for updating other game object when colliding
     *                                  with fruit.
     */
    Fruit(Vector2 topLeftCorner, Vector2 dimensions,
                 Consumer<Double> onCollisionsOtherCallback) {
        super(topLeftCorner, dimensions, new OvalRenderable(Color.RED));
        this.fruitColor = Color.RED;
        this.onCollisionsOtherCallback = onCollisionsOtherCallback;
    }

    /**
     * Handles collision events of fruit with other game objects.
     * @param other The GameObject with which a collision occurred.
     * @param collision Information regarding this collision.
     *                  A reasonable elastic behavior can be achieved with:
     *                  setVelocity(getVelocity().flipped(collision.getNormal()));
     */
    @Override
    public void onCollisionEnter(GameObject other, Collision collision) {
        super.onCollisionEnter(other, collision);
        if(other.getTag().equals(Constants.AVATAR_TAG)) {
            onCollisionsOtherCallback.accept(10.);
            Vector2 originalDimensions = new Vector2(this.getDimensions());
            this.setDimensions(Vector2.ZERO);
            new ScheduledTask(other, Constants.FULL_DAY_CYCLE_LENGTH, false,
                    () -> this.setDimensions(originalDimensions));
        }
    }

    /**
     * Updates the state of the fruit, changing it's color between red and orange.
     */
    @Override
    public void update() {
        if(fruitColor == Color.RED) {
            renderer().setRenderable(new OvalRenderable(Color.ORANGE));
            fruitColor = Color.ORANGE;
        }
        else {
            renderer().setRenderable(new OvalRenderable(Color.RED));
            fruitColor = Color.RED;
        }
    }
}
