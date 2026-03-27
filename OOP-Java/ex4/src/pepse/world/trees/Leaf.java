package pepse.world.trees;

import danogl.components.Transition;
import danogl.gui.rendering.RectangleRenderable;
import danogl.util.Vector2;
import pepse.util.ColorSupplier;
import pepse.world.Block;
import pepse.world.Observer;

import java.awt.*;
import java.util.Random;

/**
 * A class representing a leaf game object in the game's world.
 * @author Meirav Levy
 */
public class Leaf extends Block implements Observer {
    private static final Color LEAF_COLOR = new Color(50, 200, 30);
    private static final Random random = new Random();

    /**
     * Constructs a leaf game object.
     * @param topLeftCorner the top left corner position of the leaf.
     */
    Leaf(Vector2 topLeftCorner) {
        super(topLeftCorner, new RectangleRenderable(ColorSupplier.approximateColor(LEAF_COLOR)));
        float randomAngle = random.nextInt(15) + 1;
        boolean isAnglePositive = random.nextBoolean();
        if(!isAnglePositive)
            randomAngle = -randomAngle;
        this.renderer().setRenderableAngle(randomAngle);
    }

    /**
     * Updates the state of the leaf, rotating it by a fixed angle.
     */
    @Override
    public void update() {
        float angleTurnSize = 90f;
        new Transition<>(this, (Float angle) ->
                this.renderer().setRenderableAngle(angle),
                this.renderer().getRenderableAngle(), this.renderer().getRenderableAngle() +
                angleTurnSize,
                Transition.LINEAR_INTERPOLATOR_FLOAT, 2.5f,
                Transition.TransitionType.TRANSITION_ONCE,
                null);
    }
}
