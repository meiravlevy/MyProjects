package pepse.world;

import danogl.GameObject;
import danogl.gui.ImageReader;
import danogl.gui.UserInputListener;
import danogl.gui.rendering.AnimationRenderable;
import danogl.gui.rendering.Renderable;
import danogl.util.Vector2;
import pepse.Constants;
import java.awt.event.KeyEvent;
import java.util.ArrayList;
import java.util.List;

/**
 * A class representing the player's character in the game's world.
 * @author Meirav Levy
 */
public class Avatar extends GameObject implements Subject{
    private static final int WIDTH = 50;
    private static final int HEIGHT = 70;
    private static final String AVATAR_IMAGE_PATH = "assets/idle_0.png";
    private static final float GRAVITY = 600;
    private static final float VELOCITY_X = 400;
    private static final float VELOCITY_Y = -650;
    private static final String[] IDLE_IMAGE_PATHS = {"assets/idle_0.png", "assets/idle_1.png",
            "assets/idle_2.png", "assets/idle_3.png"};
    private static final String[] RUN_IMAGE_PATHS = {"assets/run_0.png", "assets/run_1.png",
            "assets/run_2.png", "assets/run_3.png", "assets/run_4.png", "assets/run_5.png"};
    private static final String[] JUMP_IMAGE_PATHS = {"assets/jump_0.png", "assets/jump_1.png",
            "assets/jump_2.png", "assets/jump_3.png"};
    private static final double TIME_BETWEEN_IMAGES = 0.2;
    private static final int MAXIMUM_ENERGY = 100;

    private final UserInputListener inputListener;
    private final Renderable idleRenderable;
    private final Renderable jumpRenderable;
    private final Renderable runRenderable;
    private final List<Observer> observers = new ArrayList<>();

    private double energy;

    /**
     * Constructs an avatar game object in the game's world.
     * @param pos The initial position of the avatar in the game.
     * @param inputListener The user input listener.
     * @param imageReader The image reader for avatar graphics.
     */
    public Avatar(Vector2 pos, UserInputListener inputListener, ImageReader imageReader) {
        super(pos, Vector2.of(WIDTH, HEIGHT), imageReader.readImage(AVATAR_IMAGE_PATH,
                false));
        physics().preventIntersectionsFromDirection(Vector2.ZERO);
        transform().setAccelerationY(GRAVITY);
        this.energy = MAXIMUM_ENERGY;
        this.inputListener = inputListener;

        idleRenderable = new AnimationRenderable(IDLE_IMAGE_PATHS, imageReader,
                false, TIME_BETWEEN_IMAGES);
        jumpRenderable = new AnimationRenderable(JUMP_IMAGE_PATHS, imageReader,
                false, TIME_BETWEEN_IMAGES);
        runRenderable = new AnimationRenderable(RUN_IMAGE_PATHS, imageReader,
                false, TIME_BETWEEN_IMAGES);
    }

    /**
     * Update's the avatar's state.
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

        float xVel = 0;
        if(inputListener.isKeyPressed(KeyEvent.VK_LEFT) && energy >= 0.5)
            xVel = handleRunLeft(xVel);
        if(inputListener.isKeyPressed(KeyEvent.VK_RIGHT) && energy >= 0.5)
            xVel = handleRunRight(xVel);
        transform().setVelocityX(xVel);
        if(inputListener.isKeyPressed(KeyEvent.VK_SPACE) && getVelocity().y() == 0 && energy >= 10)
            handleJump();
        if(getVelocity().x() == 0 && getVelocity().y() == 0)
            handleIdle();
        if(!inputListener.isKeyPressed(KeyEvent.VK_LEFT) && !inputListener.isKeyPressed(KeyEvent.VK_RIGHT) &&
                !inputListener.isKeyPressed(KeyEvent.VK_SPACE) && getVelocity().x() == 0 &&
                getVelocity().y()!=0)
            renderer().setRenderable(jumpRenderable);
    }

    /**
     * Registers an observer.
     * @param observer The observer to register.
     */
    @Override
    public void registerObserver(Observer observer) {
        observers.add(observer);
    }

    /**
     * Unregisters an observer.
     * @param observer The observer to unregister.
     */
    @Override
    public void unregisterObserver(Observer observer) {
        observers.remove(observer);
    }

    /**
     * updates all observers.
     */
    @Override
    public void notifyObservers() {
        for(Observer observer : observers)
            observer.update();
    }


    /**
     * Increases avatar's energy.
     * @param energyAddition The amount of energy to add.
     */
    public void addEnergy(double energyAddition) {
        energy = Math.min(MAXIMUM_ENERGY, energy + energyAddition);
    }

    /**
     * Gets the current energy of the avatar.
     * @return The current energy level.
     */
    public double getEnergy() { return energy; }

    /**
     * Determines whether the avatar should collide with another game object.
     * @param other The other GameObject.
     * @return True if the avatar should collide with the other object, and false otherwise.
     */
    @Override
    public boolean shouldCollideWith(GameObject other) {
        if(other.getTag().equals(Constants.LEAF_TAG)) {
            return false;
        }
        return super.shouldCollideWith(other);
    }

    /*
     * Handles avatar's state when moving left.
     */
    private float handleRunLeft(float xVel) {
        xVel -= VELOCITY_X;
        energy -= 0.5;
        renderer().setRenderable(runRenderable);
        renderer().setIsFlippedHorizontally(true);
        return xVel;
    }

    /*
     * Handles avatar's state when moving right.
     */
    private float handleRunRight(float xVel) {
        xVel += VELOCITY_X;
        energy -= 0.5;
        renderer().setRenderable(runRenderable);
        renderer().setIsFlippedHorizontally(false);
        return xVel;
    }

    /*
     * Handles avatar's state when jumping.
     */
    private void handleJump() {
        transform().setVelocityY(VELOCITY_Y);
        energy -= 10;
        renderer().setRenderable(jumpRenderable);
        notifyObservers();
    }

    /*
     * handles avatar's state when not moving.
     */
    private void handleIdle() {
        energy = Math.min(MAXIMUM_ENERGY, energy + 1);
        renderer().setRenderable(idleRenderable);
    }


}
