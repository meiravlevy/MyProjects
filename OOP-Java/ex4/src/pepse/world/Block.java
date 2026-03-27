package pepse.world;

import danogl.GameObject;
import danogl.components.GameObjectPhysics;
import danogl.gui.rendering.Renderable;
import danogl.util.Vector2;

/**
 * A class representing a block in the game's world with fixed size.
 * @author Meirav Levy
 */
public class Block extends GameObject {

    /**
     * The size of a block.
     */
    public static final int SIZE = 30;

    /**
     * Constructs a block game object in the game's world.
     * @param topLeftCorner The position of top left corner of the block.
     * @param renderable The renderable representing the object.
     */
    public Block(Vector2 topLeftCorner, Renderable renderable) {
        super(topLeftCorner, Vector2.ONES.mult(SIZE), renderable);
        physics().preventIntersectionsFromDirection(Vector2.ZERO);
        physics().setMass(GameObjectPhysics.IMMOVABLE_MASS);
    }
}
