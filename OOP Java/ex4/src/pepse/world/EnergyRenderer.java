package pepse.world;

import danogl.GameObject;
import danogl.gui.rendering.TextRenderable;
import danogl.util.Vector2;
import pepse.Constants;
import java.util.function.Supplier;

/**
 * A class representing a renderer for displaying energy level of a game object.
 * @author Meirav Levy
 */
public class EnergyRenderer extends GameObject {
    private final TextRenderable textRenderable;
    private final Supplier<Double> energyCallback;

    /**
     * Construct a new GameObject instance.
     *
     * @param topLeftCorner Position of the object, in window coordinates (pixels).
     *                      Note that (0,0) is the top-left corner of the window.
     * @param dimensions    Width and height in window coordinates.
     * @param textRenderable    The renderable representing the object. Can be null, in which case
     *                      the GameObject will not be rendered.
     * @param energyCallback Callback function for getting the energy level to render.
     */
    public EnergyRenderer(Vector2 topLeftCorner, Vector2 dimensions, TextRenderable textRenderable,
                          Supplier<Double> energyCallback) {
        super(topLeftCorner, dimensions, textRenderable);
        this.textRenderable = textRenderable;
        this.energyCallback = energyCallback;
        this.setTag(Constants.ENERGY_RENDERER_TAG);
    }

    /**
     * Updates the energy displayed by the renderer.
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
        String energy = (int)Math.floor(energyCallback.get()) + "%";
        textRenderable.setString(energy);
    }
}
