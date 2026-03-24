package pepse.world.trees;

import danogl.GameObject;
import danogl.util.Vector2;
import pepse.Constants;
import pepse.world.Block;
import pepse.world.Observer;
import pepse.world.WindBehaviour;

import java.util.LinkedList;
import java.util.List;
import java.util.Random;
import java.util.function.Consumer;
import java.util.function.Function;

/**
 * A class that is intended to plant trees in the game's world.
 * @author Meirav Levy
 */
public class Flora {

    private static final Random random = new Random();
    private static final double THRESHOLD_FOR_PLANTING = 0.1;
    private static final double THRESHOLD_FOR_LEAF_APPEARANCE = 0.5;
    private static final double THRESHOLD_FOR_FRUIT_APPEARANCE = 0.05;
    private static final int MINIMUM_STEM_HEIGHT = 6 * Block.SIZE;
    private static final int ADDITION_TO_STEM_IN_GROUND = 2 * Block.SIZE;
    private static final float PROPORTION_OF_FRUIT_TO_LEAF_SIZE = 9f / 10;


    private final Function<Float, Float> groundHeightAtXCallback;
    private final Consumer<Double> fruitCollisionOtherCallback;
    private final Consumer<GameObject> addGameObjectsToGameCallback;


    /**
     * Constructor.
     * @param groundHeightAtXCallback callback function to get the ground height at a given x coordinate.
     * @param fruitCollisionOtherCallback callback function for updating another game object when fruit
     *                                    collides with it.
     * @param addGameObjectsToGameCallback callback function for adding game objects to the game.
     */
    public Flora(Function<Float, Float> groundHeightAtXCallback,
                 Consumer<Double> fruitCollisionOtherCallback,
                 Consumer<GameObject> addGameObjectsToGameCallback) {
        this.groundHeightAtXCallback = groundHeightAtXCallback;
        this.fruitCollisionOtherCallback = fruitCollisionOtherCallback;
        this.addGameObjectsToGameCallback = addGameObjectsToGameCallback;
    }

    /**
     * Creates a list of the parts that assemble trees(stems, leaves, fruit) in the specified range and
     * adds them to the game.
     * @param minX the minimum x coordinate for planting a tree.
     * @param maxX the maximum x coordinate for planting a tree.
     * @return a list of the trees parts as observers.
     */
    public List<Observer> createInRange(int minX, int maxX) {
        List<Stem> allTreesStems = createAllTreesStemsInRange(minX, maxX);
        List<Observer> treesParts = new LinkedList<>(allTreesStems);
        addTopOfTreePartsToAllTrees(treesParts, allTreesStems,
                THRESHOLD_FOR_LEAF_APPEARANCE, this::createLeaf);
        addTopOfTreePartsToAllTrees(treesParts, allTreesStems,
                THRESHOLD_FOR_FRUIT_APPEARANCE, this::createFruit);

        return treesParts;
    }

    /*
     * adds specific type of tree parts to the top of each tree in the provided list.
     */
    private static void addTopOfTreePartsToAllTrees(List<Observer> treesParts, List<Stem> allTreesStems,
                                                    double thresholdForAppearance,
                                                    Function<Vector2, Observer> createObjCallBack) {
        for(Stem stem: allTreesStems) {
            addGameObjectsToTopOfATree(stem.getTopLeftCorner(),
                    thresholdForAppearance, createObjCallBack, treesParts);
        }

    }

    /*
     * Creates all tree stems within the specified range.
     */
    private List<Stem> createAllTreesStemsInRange(int minX, int maxX) {
        List<Stem> stems = new LinkedList<>();
        int startX = (int)Math.ceil((float)minX / Block.SIZE) * Block.SIZE;
        for(int x = startX; x < maxX - Block.SIZE; x += Block.SIZE) {
            double toPlant = random.nextDouble();
            if(toPlant < THRESHOLD_FOR_PLANTING) {
                Stem stem = createStem(x);
                stems.add(stem);
            }
        }
        return stems;
    }

    /*
     * Creates a tree stem in the specified x coordinate.
     */
    private Stem createStem(int xPosStem) {
        int stemHeight = chooseStemHeight(xPosStem);
        Vector2 stemTopLeftCorner = Vector2.of(xPosStem,
                (float)Math.floor(groundHeightAtXCallback.apply((float)xPosStem)) - stemHeight
                        + ADDITION_TO_STEM_IN_GROUND);
        Stem stem = new Stem(stemTopLeftCorner, Vector2.of(Block.SIZE, stemHeight));
        stem.setTag(Constants.STEM_TAG);
        addGameObjectsToGameCallback.accept(stem);
        return stem;
    }

    /*
     * Chooses the height of a tree stem according to the ground height at the specified x coordinate.
     */
    private int chooseStemHeight(int xPosStem) {
        float groundHeightAtX = groundHeightAtXCallback.apply((float)xPosStem);
        if(MINIMUM_STEM_HEIGHT > (int)Math.floor(groundHeightAtX / 2))
            return MINIMUM_STEM_HEIGHT;
        return random.nextInt((int)Math.floor(groundHeightAtX / 2) - MINIMUM_STEM_HEIGHT) +
                MINIMUM_STEM_HEIGHT;
    }

    /*
     * Adds specific type of game objects to the top of tree.
     */
    private static void addGameObjectsToTopOfATree(Vector2 stemTopLeftCorner,
                                                   double thresholdForAppearance,
                                                   Function<Vector2, Observer> createObjCallback,
                                                   List<Observer> trees) {
        float stemTopOffSetFactor = 3.5f;
        int gameObjectsXStart = (int)Math.floor(stemTopLeftCorner.x() - stemTopOffSetFactor * Leaf.SIZE);
        int gameObjectsYStart = (int)Math.floor(stemTopLeftCorner.y() - stemTopOffSetFactor * Leaf.SIZE);

        int squareTopOfTreeSideSize = 8 * Leaf.SIZE;
        for (int x = gameObjectsXStart; x < gameObjectsXStart + squareTopOfTreeSideSize; x += Leaf.SIZE) {
            for (int y = gameObjectsYStart; y < gameObjectsYStart + squareTopOfTreeSideSize; y += Leaf.SIZE) {
                addGameObjectToTopOfATree(Vector2.of(x, y), trees, thresholdForAppearance,
                        createObjCallback);
            }
        }
    }

    /*
     * Adds one game object to the top of a tree.
     */
    private static void addGameObjectToTopOfATree(Vector2 objPos, List<Observer> gameObjects,
                                                  double thresholdForAppearance,
                                                  Function<Vector2, Observer> createObj) {
        double objProbability = random.nextDouble();
        if (objProbability < thresholdForAppearance) {
            Observer obj = createObj.apply(objPos);
            gameObjects.add(obj);
        }
    }

    /*
     * Creates a fruit game object and adds it to the game.
     */
    private Observer createFruit(Vector2 fruitTopLeftCorner) {
        Fruit fruit = new Fruit(fruitTopLeftCorner, Vector2.ONES.mult(
                Leaf.SIZE * PROPORTION_OF_FRUIT_TO_LEAF_SIZE),
                fruitCollisionOtherCallback);
        fruit.setTag(Constants.FRUIT_TAG);
        addGameObjectsToGameCallback.accept(fruit);
        return fruit;
    }

    /*
     * Creates a leaf game object that moves with the wind and adds it to the game.
     */
    private Observer createLeaf(Vector2 leafTopLeftCorner) {
        Leaf leaf = new Leaf(leafTopLeftCorner);
        leaf.setTag(Constants.LEAF_TAG);
        addGameObjectsToGameCallback.accept(leaf);
        WindBehaviour.applyWindEffects(leaf);
        return leaf;
    }
}