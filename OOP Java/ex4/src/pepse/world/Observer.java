package pepse.world;

/**
 * represents an object that can be observed and updated.
 * Objects implementing this interface can receive update notifications and perform necessary actions
 * accordingly.
 */
public interface Observer {

    /**
     * Updates the observer's state.
     */
    void update();
}
