package pepse.world;

import danogl.GameObject;
import danogl.components.CoordinateSpace;
import danogl.gui.rendering.RectangleRenderable;
import danogl.util.Vector2;
import pepse.Constants;

import java.awt.*;

/**
 * A class representing a sky game object in the game's world.
 * @author Meirav Levy
 */
public class Sky {
    private static final Color BASIC_SKY_COLOR = Color.decode("#80C6E5");

    /**
     * Constructor.
     */
    public Sky() {}

    /**
     * Creates the sky game object.
     * @param windowDimensions The dimensions of the game's window.
     * @return The created sky game object.
     */
    public static GameObject create(Vector2 windowDimensions) {
        GameObject sky = new GameObject(Vector2.ZERO, windowDimensions,
                new RectangleRenderable(BASIC_SKY_COLOR));
        sky.setCoordinateSpace(CoordinateSpace.CAMERA_COORDINATES);
        sky.setTag(Constants.SKY_TAG);
        return sky;
    }
}
