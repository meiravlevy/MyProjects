package pepse;

import danogl.GameManager;
import danogl.GameObject;
import danogl.collisions.Layer;
import danogl.gui.ImageReader;
import danogl.gui.SoundReader;
import danogl.gui.UserInputListener;
import danogl.gui.WindowController;
import danogl.gui.rendering.TextRenderable;
import danogl.util.Vector2;
import pepse.world.*;
import pepse.world.Avatar;
import pepse.world.daynight.Night;
import pepse.world.daynight.Sun;
import pepse.world.daynight.SunHalo;
import pepse.world.trees.Flora;

import java.util.List;
import java.util.Random;
import java.util.function.Function;

/**
 * This class represents the main game manager for the Pepse game.
 * Manages the initialization and setup of game elements.
 * @author Meirav Levy
 */
public class PepseGameManager extends GameManager {
    private static final Random random = new Random();

    /**
     * Initializes the game, including setting up all game objects.
     * @param imageReader Contains a single method: readImage, which reads an image from disk.
     *                 See its documentation for help.
     * @param soundReader Contains a single method: readSound, which reads a wav file from
     *                    disk. See its documentation for help.
     * @param inputListener Contains a single method: isKeyPressed, which returns whether
     *                      a given key is currently pressed by the user or not. See its
     *                      documentation.
     * @param windowController Contains an array of helpful, self-explanatory methods
     *                         concerning the window.
     */
    @Override
    public void initializeGame(ImageReader imageReader, SoundReader soundReader,
                               UserInputListener inputListener, WindowController windowController) {
        super.initializeGame(imageReader, soundReader, inputListener, windowController);
        Vector2 windowDimensions = windowController.getWindowDimensions();

        createSky(windowDimensions);
        Terrain terrain = createBlocks(windowDimensions);
        createNight(windowDimensions);
        GameObject sun = createSun(windowDimensions);
        createSunHalo(sun);
        Avatar avatar = createAvatar(windowDimensions, terrain, imageReader, inputListener);
        createEnergyRenderer(avatar);
        createTrees(windowDimensions, terrain::groundHeightAt, avatar);

    }

    /**
     * The entry point to the Pepse game.
     * @param args command-line arguments(not used).
     */
    public static void main(String[] args) {new PepseGameManager().run();}

    /*
     * Creates the sky game object and adds it to the game.
     */
    private void createSky(Vector2 windowDimensions) {
        GameObject sky = Sky.create(windowDimensions);
        gameObjects().addGameObject(sky, Layer.BACKGROUND);
    }

    /*
     * Creates the terrain blocks and adds them to the game.
     */
    private Terrain createBlocks(Vector2 windowDimensions) {
        Terrain terrain = new Terrain(windowDimensions, (int)random.nextGaussian());
        List<Block> blocks = terrain.createInRange(0, (int) Math.ceil(windowDimensions.x()));
        for(GameObject block : blocks)
            gameObjects().addGameObject(block, Layer.STATIC_OBJECTS);
        return terrain;
    }

    /*
     * Creates the night game object and adds it to the game.
     */
    private void createNight(Vector2 windowDimensions) {
        GameObject night = Night.create(windowDimensions, Constants.FULL_DAY_CYCLE_LENGTH);
        gameObjects().addGameObject(night, Layer.FOREGROUND);
    }

    /*
     * Creates the sun game object and adds it to the game.
     */
    private GameObject createSun(Vector2 windowDimensions) {
        GameObject sun = Sun.create(windowDimensions, Constants.FULL_DAY_CYCLE_LENGTH);
        gameObjects().addGameObject(sun, Layer.BACKGROUND);
        return sun;
    }

    /*
     * Creates the sun's halo game object and adds it to the game.
     */
    private void createSunHalo(GameObject sun) {
        GameObject sunHalo = SunHalo.create(sun);
        gameObjects().addGameObject(sunHalo, Layer.BACKGROUND);
    }

    /*
     * Creates the avatar game object and adds it to the game.
     */
    private Avatar createAvatar(Vector2 windowDimensions, Terrain terrain, ImageReader imageReader,
                                UserInputListener inputListener) {
        Avatar avatar = new Avatar(Vector2.of(windowDimensions.x() / 2,
                (float)Math.floor(terrain.groundHeightAt(windowDimensions.x() / 2) / Block.SIZE)
                        * Block.SIZE - Block.SIZE), inputListener, imageReader);
        avatar.setTag(Constants.AVATAR_TAG);
        gameObjects().addGameObject(avatar);
        return avatar;
    }

    /*
     * Creates the energy renderer game object and adds it to the game/
     */
    private void createEnergyRenderer(Avatar avatar) {
        TextRenderable textRenderable = new TextRenderable("");
        GameObject energyRenderer = new EnergyRenderer(Vector2.ZERO, Vector2.of(50, 40), textRenderable,
                avatar::getEnergy);
        gameObjects().addGameObject(energyRenderer, Layer.UI);
    }

    /*
     * Creates the flora of the game and adds the game objects that are created by flora to the game, plus
     * adds them as observers of the avatar.
     */
    private void createTrees(Vector2 windowDimensions, Function<Float, Float> groundHeightAtCallback,
                             Avatar avatar) {
        Flora flora = new Flora(groundHeightAtCallback, avatar::addEnergy, this::addTreePart);
        List<Observer> treesParts = flora.createInRange(0, (int) Math.ceil(windowDimensions.x()));
        for(Observer observer: treesParts) {
            avatar.registerObserver(observer);
        }
    }

    /*
     * adds a tree part game object to the game.
     */
    private void addTreePart(GameObject part) { gameObjects().addGameObject(part, Layer.STATIC_OBJECTS);}

}