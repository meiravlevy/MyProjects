package pepse.world.daynight;

import danogl.GameObject;
import danogl.components.CoordinateSpace;
import danogl.components.Transition;
import danogl.gui.rendering.OvalRenderable;
import danogl.gui.rendering.Renderable;
import danogl.util.Vector2;
import pepse.Constants;
import java.awt.*;

/**
 * Represents the sun game object in the full day cycle of the game.
 * @author Meirav Levy
 */
public class Sun {
    private static final int SIZE = 80;

    /**
     * Constructor.
     */
    public Sun() {}

    /**
     * Creates the sun game object.
     * @param windowDimensions the dimensions of the game window.
     * @param cycleLength the length of a full day cycle.
     * @return the created sun game object.
     */
    public static GameObject create(Vector2 windowDimensions, float cycleLength) {
        Renderable renderable = new OvalRenderable(Color.YELLOW);
        GameObject sun = new GameObject(Vector2.ZERO, Vector2.ONES.mult(SIZE), renderable);
        Vector2 initialSunCenter = new Vector2(windowDimensions.x() / 2,
                windowDimensions.y() * Constants.PROPORTION_OF_GROUND_TO_WINDOW_DIMENSIONS * 0.5f);
        sun.setCenter(initialSunCenter);
        sun.setCoordinateSpace(CoordinateSpace.CAMERA_COORDINATES);
        sun.setTag(Constants.SUN_TAG);

        rotateSunInACircle(sun, windowDimensions, initialSunCenter, cycleLength);
        return sun;
    }

    /*
     * Rotates the sun game object in a circular motion around a fixed point.
     */
    private static void rotateSunInACircle(GameObject sun, Vector2 windowDimensions, Vector2 initialSunCenter,
                                    float cycleLength) {
        Vector2 cycleCenter = new Vector2(windowDimensions.x() / 2,
                windowDimensions.y() * Constants.PROPORTION_OF_GROUND_TO_WINDOW_DIMENSIONS);
        new Transition<> (sun,
                (Float angle) -> sun.setCenter(initialSunCenter.subtract(cycleCenter)
                        .rotated(angle).add(cycleCenter)), 0f, 360f,
                Transition.LINEAR_INTERPOLATOR_FLOAT, cycleLength,
                Transition.TransitionType.TRANSITION_LOOP, null);
    }
}
