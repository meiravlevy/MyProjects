package pepse.world;

import danogl.gui.rendering.RectangleRenderable;
import danogl.util.Vector2;
import pepse.Constants;
import pepse.util.ColorSupplier;
import pepse.util.NoiseGenerator;

import java.awt.*;
import java.util.LinkedList;
import java.util.List;

/**
 * Represents The terrain in the game's world.
 * @author Meirav Levy
 */
public class Terrain {
    private static final Color BASE_GROUND_COLOR = new Color(212, 123, 74);
    private static final int TERRAIN_DEPTH = 20;
    private final float groundHeightAtX0;
    private final Vector2 windowDimensions;
    private final NoiseGenerator noiseGenerator;

    /**
     * Constructs the terrain in the game's world.
     * @param windowDimensions The dimensions of the game's window.
     * @param seed The seed value for noise generation.
     */
    public Terrain(Vector2 windowDimensions, int seed) {
        this.windowDimensions = windowDimensions;
        this.groundHeightAtX0 = (int)Math.floor((windowDimensions.y() *
                Constants.PROPORTION_OF_GROUND_TO_WINDOW_DIMENSIONS));
        this.noiseGenerator = new NoiseGenerator(seed, (int)this.groundHeightAtX0);
    }

    /**
     * Gets the ground height at a specifies x coordinate.
     * @param x The x coordinate.
     * @return The ground height at the x coordinate.
     */
    public float groundHeightAt(float x) {
        float noise = (float) noiseGenerator.noise(x, Block.SIZE * 7);
        return groundHeightAtX0 + noise;
    }


    /**
     * Creates a list of blocks in the specified range.
     * @param minX The minimum x coordinate.
     * @param maxX The maximum x coordinate.
     * @return The list of blocks created within the specified range.
     */
    public List<Block> createInRange(int minX, int maxX) {
        List<Block> blocksList = new LinkedList<>();

        int startX = (int)Math.floor((float)minX / Block.SIZE) * Block.SIZE;
        for (int i = startX; i < maxX; i += Block.SIZE) {
            float startY = (float)Math.min(Math.floor(groundHeightAt(i) / Block.SIZE) * Block.SIZE,
                    windowDimensions.y() - Block.SIZE);
            for (int j = 0; j < TERRAIN_DEPTH; j++) {
                startY += Block.SIZE;
                Block block = new Block(new Vector2(i, startY),
                        new RectangleRenderable(ColorSupplier.approximateColor(BASE_GROUND_COLOR)));
                block.setTag(Constants.BLOCK_TAG);
                blocksList.add(block);
            }
        }

        return blocksList;
    }

}