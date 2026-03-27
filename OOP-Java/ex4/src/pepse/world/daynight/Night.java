package pepse.world.daynight;

import danogl.GameObject;
import danogl.components.CoordinateSpace;
import danogl.components.Transition;
import danogl.gui.rendering.RectangleRenderable;
import danogl.gui.rendering.Renderable;
import danogl.util.Vector2;
import pepse.Constants;

import java.awt.*;

/**
 * Represents the night phase in the full day cycle of the game.
 * @author Meirav Levy
 */
public class Night {
    private static final float MIDNIGHT_OPACITY = 0.5f;

    /**
     * Constructor.
     */
    public Night() {}

    /**
     * Creates the night game object.
     * @param windowDimensions the dimensions of the game's window.
     * @param cycleLength the length of a full day cycle.
     * @return the created night game object.
     */
    public static GameObject create(Vector2 windowDimensions, float cycleLength) {
        Renderable renderable = new RectangleRenderable(Color.BLACK);
        GameObject night = new GameObject(Vector2.ZERO, windowDimensions, renderable);
        night.setCoordinateSpace(CoordinateSpace.CAMERA_COORDINATES);
        night.setTag(Constants.NIGHT_TAG);
        new Transition<> (night, night.renderer()::setOpaqueness, 0f, MIDNIGHT_OPACITY,
                Transition.CUBIC_INTERPOLATOR_FLOAT, cycleLength / 2,
                Transition.TransitionType.TRANSITION_BACK_AND_FORTH, null);
        return night;
    }
}
