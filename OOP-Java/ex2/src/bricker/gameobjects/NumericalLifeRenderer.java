package bricker.gameobjects;

import bricker.main.BrickerGameManager;
import danogl.GameObject;
import danogl.gui.rendering.TextRenderable;
import danogl.util.Vector2;

import java.awt.*;

/**
 * A class used for rendering the lives in the game in numerical text.
 * @author Meirav Levy
 */
public class NumericalLifeRenderer extends GameObject {

    private final TextRenderable textRenderable;
    private final BrickerGameManager brickerGameManager;

    /**
     * Construct a new GameObject instance.
     *
     * @param topLeftCorner  Position of the object, in window coordinates (pixels).
     *                       Note that (0,0) is the top-left corner of the window.
     * @param dimensions     Width and height in window coordinates.
     * @param textRenderable The renderable representing the object. Can be null, in which case
     *                       the GameObject will not be rendered.
     * @param brickerGameManager bricker game manager.
     */
    public NumericalLifeRenderer(Vector2 topLeftCorner, Vector2 dimensions, TextRenderable textRenderable,
                                 BrickerGameManager brickerGameManager) {
        super(topLeftCorner, dimensions, textRenderable);
        this.textRenderable = textRenderable;
        this.brickerGameManager = brickerGameManager;
    }

    /**
     * Renders the lives currently in the game numerically.
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
        String numOfLivesStr = String.valueOf(brickerGameManager.getNumOfLivesInGame());
        textRenderable.setString(numOfLivesStr);
        if(brickerGameManager.getNumOfLivesInGame() == 1)
            textRenderable.setColor(Color.RED);
        else if(brickerGameManager.getNumOfLivesInGame() == 2)
            textRenderable.setColor(Color.YELLOW);
        else
            textRenderable.setColor(Color.GREEN);
    }
}
