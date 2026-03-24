package ascii_art;

/**
 * A class for an exception that occurs when a command is invalid.
 * @author Meirav Levy
 */
public class InvalidCommandException extends Exception{
    /**
     * constructor.
     * @param message message of the exception.
     */
    public InvalidCommandException(String message) {
        super(message);
    }
}
