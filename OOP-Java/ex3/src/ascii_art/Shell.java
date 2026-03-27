package ascii_art;


import ascii_output.AsciiOutput;
import ascii_output.ConsoleAsciiOutput;
import ascii_output.HtmlAsciiOutput;
import image.Image;
import image.ImageProcessor;
import image_char_matching.SubImgCharMatcher;
import java.io.IOException;
import java.util.ArrayList;

/**
 * Class intended for user interface where he can change parameters for asciiArt and execute it.
 * @author Meirav Levy
 */
public class Shell {
    private static final String PROMPT = ">>> ";
    private static final String EXIT_COMMAND = "exit";
    private static final String SEE_CHARS_COMMAND = "chars";
    private static final String CHARS_PRINT_SEPARATOR = " ";
    private static final String ADD_COMMAND_PREFIX = "add ";
    private static final String REMOVE_COMMAND_PREFIX = "remove ";
    private static final String COMMAND_POSTFIX_ALL = "all";
    private static final String COMMAND_POSTFIX_SPACE = "space";
    private static final String RESOLUTION_PREFIX_COMMAND = "res ";
    private static final String RESOLUTION_PLACEHOLDER = "<current resolution>";
    private static final String RESOLUTION_UPDATED_MSG = "Resolution set to <current resolution>.";
    private static final String RESOLUTION_UP_POSTFIX = "up";
    private static final String RESOLUTION_DOWN_POSTFIX = "down";
    private static final String IMAGE_COMMAND_PREFIX = "image ";
    private static final String OUTPUT_COMMAND_PREFIX = "output ";
    private static final String OUTPUT_CONSOLE_POSTFIX = "console";
    private static final String OUTPUT_HTML_POSTFIX = "html";
    private static final String HTML_FILE_NAME = "out.html";
    private static final String HTML_FONT = "Courier New";
    private static final String ASCII_ART_COMMAND = "asciiArt";

    private static final String ERROR_MSG_INCORRECT_ADD_FORMAT = "Did not add due to incorrect format.";
    private static final String ERROR_MSG_INCORRECT_REMOVE_FORMAT = "Did not remove due to incorrect format.";
    private static final String ERROR_MSG_INCORRECT_RESOLUTION_FORMAT = "Did not change resolution due to " +
            "incorrect format.";
    private static final String ERROR_MSG_IMAGE_EXECUTION = "Did not execute due to problem with image file.";
    private static final String ERROR_MSG_RES_EXCEEDING_BOUNDARIES = "Did not change resolution due to " +
            "exceeding boundaries.";
    private static final String ERROR_MSG_OUTPUT_FORMAT = "Did not change output method due to incorrect " +
            "format.";
    private static final String ERROR_MSG_ASCII_ART = "Did not execute. Charset is empty.";
    private static final String ERROR_MSG_INCORRECT_COMMAND = "Did not execute due to incorrect command.";
    private static final char CHAR_RANGE_DELIMITER = '-';
    private static final int FIRST_KEYBOARD_ASCII_NUM = 32;
    private static final int LAST_KEYBOARD_ASCII_NUM = 126;
    private static final int DEFAULT_RESOLUTION = 128;
    private static final int NUM_OF_CHARS_IN_RANGE_OF_CHARS_COMMAND = 3;
    private static final String DEFAULT_IMAGE_PATH = "cat.jpeg";

    private final SubImgCharMatcher subImgCharMatcher;

    private String imagePath;
    private boolean didImageOrResolutionChange;
    private AsciiOutput output;
    private Image paddedImage;
    private int resolution;
    private ArrayList<Image> subImages;

    /**
     * Constructor.
     */
    public Shell() {
        char[] charset = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'};
        subImgCharMatcher = new SubImgCharMatcher(charset);
        this.resolution = DEFAULT_RESOLUTION;
        this.output = new ConsoleAsciiOutput();
        this.imagePath = DEFAULT_IMAGE_PATH;
        this.didImageOrResolutionChange = false;
    }

    /**
     * Runs a user interface for changing parameters for the asciiArt and executing asciiArt.
     */
    public void run() {
        try {
            Image image = new Image(DEFAULT_IMAGE_PATH);
            paddedImage = ImageProcessor.padImage(image);
        }
        catch (IOException e){
            System.out.println(ERROR_MSG_IMAGE_EXECUTION);
        }
        System.out.print(PROMPT);
        String keyboardInputStr = KeyboardInput.readLine();
        while(!keyboardInputStr.equals(EXIT_COMMAND)) {
            if (keyboardInputStr.equals(SEE_CHARS_COMMAND))
                seeChars();
            else if (keyboardInputStr.startsWith(ADD_COMMAND_PREFIX))
                add(keyboardInputStr.replaceFirst(ADD_COMMAND_PREFIX, ""));
            else if (keyboardInputStr.startsWith(REMOVE_COMMAND_PREFIX))
                remove(keyboardInputStr.replaceFirst(REMOVE_COMMAND_PREFIX, ""));
            else if (keyboardInputStr.startsWith(RESOLUTION_PREFIX_COMMAND))
                updateResolution(keyboardInputStr.replaceFirst(RESOLUTION_PREFIX_COMMAND, ""));
            else if(keyboardInputStr.startsWith(IMAGE_COMMAND_PREFIX))
                changeImage(keyboardInputStr.replaceFirst(IMAGE_COMMAND_PREFIX, ""));
            else if(keyboardInputStr.startsWith(OUTPUT_COMMAND_PREFIX))
                changeOutput(keyboardInputStr.replaceFirst(OUTPUT_COMMAND_PREFIX, ""));
            else if(keyboardInputStr.equals(ASCII_ART_COMMAND))
                executeAsciiArt();
            else
                handleIncorrectCommand();
            System.out.print(PROMPT);
            keyboardInputStr = KeyboardInput.readLine();
        }
    }

    /**
     * the main function that runs the shell.
     * @param args arguments from command line.
     */
    public static void main(String[] args) {

        Shell shell = new Shell();
        shell.run();
    }

    /*
     * Handles incorrect command given by the user.
     */
    private static void handleIncorrectCommand() {
        try {
            throw new InvalidCommandException(ERROR_MSG_INCORRECT_COMMAND);
        }
        catch(InvalidCommandException e) {
            System.out.println(e.getMessage());
        }
    }

    /*
     * Checks if a command of range of chars is in the right format. Returns true if it is, and false
     * otherwise.
     */
    private static boolean isCommandRangeOfChars(String command) {
        return command.length() == NUM_OF_CHARS_IN_RANGE_OF_CHARS_COMMAND &&
                command.charAt(1) == CHAR_RANGE_DELIMITER;
    }

    /*
     * Executes the asciiArt algorithm. If the charset of the sub images char matcher is empty, it prints
     * an error.
     */
    private void executeAsciiArt() {
        try {
            char[] charsetUsed = subImgCharMatcher.getCharsUsed();
            if(charsetUsed.length == 0)
                throw new InvalidCommandException(ERROR_MSG_ASCII_ART);
            if(didImageOrResolutionChange || subImages == null) {
                subImages = ImageProcessor.divideImageToSubImages(paddedImage, resolution);
            }
            AsciiArtAlgorithm asciiArtAlgorithm = new AsciiArtAlgorithm(
                    subImgCharMatcher, subImages, resolution);
            char[][] imageInChars = asciiArtAlgorithm.run();
            output.out(imageInChars);
            didImageOrResolutionChange = false;
        }
        catch(InvalidCommandException e) {
            System.out.println(e.getMessage());
        }
    }

    /*
     * Changes the way that the asciiArt is outputted. Prints an error if the output postfix isn't in the
     * right format.
     */
    private void changeOutput(String outputPostfix) {
        try {
            if(outputPostfix.equals(OUTPUT_CONSOLE_POSTFIX))
                output = new ConsoleAsciiOutput();
            else if(outputPostfix.equals(OUTPUT_HTML_POSTFIX))
                output = new HtmlAsciiOutput(HTML_FILE_NAME, HTML_FONT);
            else
                throw new IncorrectFormatException(ERROR_MSG_OUTPUT_FORMAT);
        }
        catch (IncorrectFormatException e) {
            System.out.println(e.getMessage());
        }
    }

    /*
     * changes the image to be processed. If there is a problem with the image, it prints an error to the
     * console.
     */
    private void changeImage(String imagePostfix) {
        try{
            if(!imagePostfix.equals(imagePath)) {
                imagePath = imagePostfix;
                Image image = new Image(imagePostfix);
                paddedImage = ImageProcessor.padImage(image);
                didImageOrResolutionChange = true;
            }
        }
        catch (IOException e) {
            System.out.println(ERROR_MSG_IMAGE_EXECUTION);
        }
    }

    /*
     * updates the resolution. In case that the command isn't valid, it prints the error and doesn't update
     *  the resolution.
     */
    private void updateResolution(String resPostfix) {
        try {
            if(!resPostfix.equals(RESOLUTION_UP_POSTFIX) && !resPostfix.equals(RESOLUTION_DOWN_POSTFIX))
                throw new IncorrectFormatException(ERROR_MSG_INCORRECT_RESOLUTION_FORMAT);
            if(resPostfix.equals(RESOLUTION_UP_POSTFIX))
                updateResolutionUp(paddedImage);
            else
                updateResolutionDown(paddedImage);
        }
        catch(IncorrectFormatException | InvalidCommandException e) {
            System.out.println(e.getMessage());
        }
    }

    /*
     * Increases the resolution. if resolution can't be increased, it throws an error.
     */
    private void updateResolutionUp(Image paddedImage) throws InvalidCommandException{
        int maxCharsInARow = paddedImage.getWidth();
        if((resolution * 2) > maxCharsInARow)
            throw  new InvalidCommandException(ERROR_MSG_RES_EXCEEDING_BOUNDARIES);
        resolution *= 2;
        didImageOrResolutionChange = true;
        System.out.println(RESOLUTION_UPDATED_MSG.replaceFirst(
                RESOLUTION_PLACEHOLDER, String.valueOf(resolution)));
    }

    /*
     * Decreases the resolution. in case that the resolution can't be decreased, it throws an error.
     */
    private void updateResolutionDown(Image paddedImage) throws InvalidCommandException {
        int minCharsInRow = Math.max(1, paddedImage.getWidth() / paddedImage.getHeight());
        if((resolution / 2) < minCharsInRow)
            throw new InvalidCommandException(ERROR_MSG_RES_EXCEEDING_BOUNDARIES);
        resolution /= 2;
        didImageOrResolutionChange = true;
        System.out.println(RESOLUTION_UPDATED_MSG.replaceFirst(
                RESOLUTION_PLACEHOLDER, String.valueOf(resolution)));

    }

    /*
     * removes characters from the charset used for the asciiArt. In the case of an invalid command, it
     * prints an error to the console.
     */
    private void remove(String removePostfix) {
        try {
            if (removePostfix.length() == 1)
                subImgCharMatcher.removeChar(removePostfix.charAt(0));
            else if (removePostfix.equals(COMMAND_POSTFIX_SPACE))
                subImgCharMatcher.removeChar(' ');
            else if (removePostfix.equals(COMMAND_POSTFIX_ALL))
                removeRangeOfChars(FIRST_KEYBOARD_ASCII_NUM, LAST_KEYBOARD_ASCII_NUM);
            else if (isCommandRangeOfChars(removePostfix)) {
                removeRangeOfChars(removePostfix.charAt(0), removePostfix.charAt(removePostfix.length() - 1));
            }
            else
                throw new IncorrectFormatException(ERROR_MSG_INCORRECT_REMOVE_FORMAT);
        }
        catch(IncorrectFormatException e) {
            System.out.println(e.getMessage());
        }

    }

    /*
     * Adds characters to the charset used for the asciiArt. In the case of an invalid command, it prints
     * an error to the console.
     */
    private void add(String addPostfix) {
        try {
            if (addPostfix.length() == 1)
                subImgCharMatcher.addChar(addPostfix.charAt(0));
            else if (addPostfix.equals(COMMAND_POSTFIX_SPACE))
                subImgCharMatcher.addChar(' ');
            else if (addPostfix.equals(COMMAND_POSTFIX_ALL))
                addRangeOfChars(FIRST_KEYBOARD_ASCII_NUM, LAST_KEYBOARD_ASCII_NUM);
            else if (isCommandRangeOfChars(addPostfix))
                addRangeOfChars(addPostfix.charAt(0), addPostfix.charAt(addPostfix.length() - 1));
            else
                throw new IncorrectFormatException(ERROR_MSG_INCORRECT_ADD_FORMAT);
        }
        catch (IncorrectFormatException e) {
            System.out.println(e.getMessage());
        }
    }

    /*
     * Removes a range of characters from the charset used for the asciiArt.
     */
    private void removeRangeOfChars(int firstChar, int lastChar) {
        int minChar = Math.min(firstChar, lastChar);
        int maxChar = Math.max(firstChar, lastChar);
        for(int i = minChar; i <= maxChar; i++) {
            subImgCharMatcher.removeChar((char)i);
        }
    }

    /*
     * Adds a range of characters to the charset used for the asciiArt.
     */
    private void addRangeOfChars(int firstChar, int lastChar) {
        int minChar = Math.min(firstChar, lastChar);
        int maxChar = Math.max(firstChar, lastChar);
        for(int i = minChar; i <= maxChar; i++) {
            subImgCharMatcher.addChar((char)i);
        }
    }

    /*
     * Prints all characters of the charset used for the asciiArt.
     */
    private void seeChars() {
        char[] chars = subImgCharMatcher.getCharsUsed();
        for(char c: chars) {
            System.out.print(c + CHARS_PRINT_SEPARATOR);
        }
        System.out.println();
    }
}
