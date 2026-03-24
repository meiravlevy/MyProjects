package pepse.world.daynight;

import danogl.GameObject;
import danogl.components.CoordinateSpace;
import danogl.gui.rendering.OvalRenderable;
import danogl.gui.rendering.Renderable;
import danogl.util.Vector2;
import pepse.Constants;

import java.awt.*;

/**
 * Represents the halo around the sun in a full day cycle of the game.
 * @author Meirav Levy
 */
public class SunHalo {
    private static final int SIZE = 170;
    private static final Color SUN_HALO_COLOR = new Color(255, 255, 0, 20);

    /**
     * Constructor.
     */
    public SunHalo() {}

    /**
     * Creates the sun halo game object.
     * @param sun the sun game object in which the halo is created around.
     * @return the created sun halo game object.
     */
    public static GameObject create(GameObject sun) {
        Renderable renderable = new OvalRenderable(SUN_HALO_COLOR);
        GameObject sunHalo = new GameObject(Vector2.ZERO,
                Vector2.ONES.mult(SIZE), renderable);
        sunHalo.setCoordinateSpace(CoordinateSpace.CAMERA_COORDINATES);
        sunHalo.setTag(Constants.SUN_HALO_TAG);
        sunHalo.addComponent((float deltaTime) -> sunHalo.setCenter(sun.getCenter()));
        return sunHalo;
    }
}
