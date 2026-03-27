package bricker.gameobjects;

import bricker.main.BrickerGameManager;
import bricker.main.Constants;
import danogl.GameObject;
import danogl.gui.rendering.Renderable;
import danogl.util.Vector2;

/**
 * A class used for rendering the remaining lives in the game graphically.
 * @author Meirav Levy
 */
public class GraphicLifeRenderer extends GameObject {
    private final BrickerGameManager brickerGameManager;
    private final GameObject[] lives;
    private int numOfLivesDisplayed;
    private float lifeXStart;

    /**
     * Construct a new GameObject instance.
     *
     * @param topLeftCorner      Position of the object, in window coordinates (pixels).
     *                           Note that (0,0) is the top-left corner of the window.
     * @param dimensions         Width and height in window coordinates.
     * @param renderable         The renderable representing the object. Can be null, in which case
     *                           the GameObject will not be rendered.
     * @param brickerGameManager bricker game manager.
     */
    public GraphicLifeRenderer(Vector2 topLeftCorner, Vector2 dimensions, Renderable renderable,
                               BrickerGameManager brickerGameManager) {
        super(topLeftCorner, dimensions, renderable);
        this.numOfLivesDisplayed = 0;
        this.brickerGameManager = brickerGameManager;
        this.lives = new GameObject[Constants.MAX_NUM_OF_LIVES];
        this.lifeXStart =  getTopLeftCorner().x();
        addLivesToDisplay();
    }

    /**
     * Removes or adds lives to the display according to the current lives in the game.
     * Should be called once per frame.
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
        if(brickerGameManager.getNumOfLivesInGame() < numOfLivesDisplayed) {
            removeLife();

        }
        if(brickerGameManager.getNumOfLivesInGame() > numOfLivesDisplayed) {
            addLife();
        }
    }
    /*
     * Adds the amount of lives in the game to the graphic display.
     */
    private void addLivesToDisplay() {
        while(numOfLivesDisplayed < brickerGameManager.getNumOfLivesInGame()) {
            addLife();
        }
    }
    /*
     * Adds one life to display.
     */
    private void addLife() {
        GameObject life = new GameObject(new Vector2(lifeXStart, getTopLeftCorner().y()),
                this.getDimensions(), renderer().getRenderable());
        life.setTag(Constants.REGULAR_LIFE_TAG);
        brickerGameManager.addGameObject(life);
        numOfLivesDisplayed += 1;
        lives[numOfLivesDisplayed - 1] = life;
        lifeXStart += this.getDimensions().x() + Constants.SPACE_BETWEEN_LIVES;
    }
    /*
     * Remove one life from the display.
     */
    private void removeLife() {
        brickerGameManager.removeGameObject(lives[numOfLivesDisplayed - 1]);
        numOfLivesDisplayed -= 1;
        lifeXStart -= this.getDimensions().x() + Constants.SPACE_BETWEEN_LIVES;
    }

}
