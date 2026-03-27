package pepse.world;

/**
 * A subject interface for the observers to update according to it.
 * Objects implementing this interface can register, unregister, and notify the observers of a change that
 * has occurred.
 */
public interface Subject {
    /**
     * Registers an observer.
     * @param observer The observer to register.
     */
    void registerObserver(Observer observer);

    /**
     * Unregisters an observer.
     * @param observer The observer to unregister.
     */
    void unregisterObserver(Observer observer);

    /**
     * updates all observers.
     */
    void notifyObservers();

}
