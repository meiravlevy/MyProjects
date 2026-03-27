package pepse.world.trees;

import danogl.GameObject;
import danogl.components.GameObjectPhysics;
import danogl.gui.rendering.RectangleRenderable;
import danogl.util.Vector2;
import pepse.util.ColorSupplier;
import pepse.world.Observer;
import java.awt.*;

/**
 * A class representing a stem game object in the game's world.
 */
public class Stem extends GameObject implements Observer {
    private final Color stemColorVariant;

    /**
     * Constructs a stem game object in the game's world.
     * @param topLeftCorner the top left corner position of the stem.
     * @param dimensions the width and height of the stem.
     */
    Stem(Vector2 topLeftCorner, Vector2 dimensions) {
        super(topLeftCorner, dimensions,
                new RectangleRenderable(ColorSupplier.approximateColor(new Color(100, 50, 20))));
        this.stemColorVariant = new Color(100, 50, 20);
        physics().preventIntersectionsFromDirection(Vector2.ZERO);
        physics().setMass(GameObjectPhysics.IMMOVABLE_MASS);
    }

    /**
     * Updates the state of the stem, changing it's color to a different shade of brown.
     */
    @Override
    public void update() {
        renderer().setRenderable(new RectangleRenderable(ColorSupplier.approximateColor(stemColorVariant)));
    }
}
