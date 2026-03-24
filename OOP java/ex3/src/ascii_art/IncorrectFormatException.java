package ascii_art;

/**
 * A class for an exception that occurs when a string is in the wrong format.
 */
public class IncorrectFormatException extends Exception{
    /**
     * constructor.
     * @param message message of the exception.
     */
    public IncorrectFormatException(String message) {super(message);}
}
