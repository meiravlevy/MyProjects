package image_char_matching;


import java.util.*;

/**
 * A class that matches between an image and a character according to their brightness.
 * @author Meirav Levy
 */
public class SubImgCharMatcher {
    private static final int NUM_OF_ASCII_CHARS = 128;
    private static final double DEFAULT_IF_BRIGHTNESS_NOT_COMPUTED = -1;
    private char charWithMinBrightness = (char)0;
    private char charWithMaxBrightness = (char)0;
    private final double[] charsBrightness; // brightnesses of only the characters used for matching.
    private final double[] allCharsBrightness; // brightnesses of all characters that were computed.
    private final TreeMap<Double, PriorityQueue<Character>> normalizedBrightnessChars;


    /**
     * Constructor.
     * @param charset the array of characters to use for matching with images.
     */
   public SubImgCharMatcher(char[] charset) {
       charsBrightness = new double[NUM_OF_ASCII_CHARS];
       allCharsBrightness = new double[NUM_OF_ASCII_CHARS];
       this.normalizedBrightnessChars = new TreeMap<>();
       Arrays.fill(this.charsBrightness, DEFAULT_IF_BRIGHTNESS_NOT_COMPUTED);
       Arrays.fill(this.allCharsBrightness, DEFAULT_IF_BRIGHTNESS_NOT_COMPUTED);
       for(char c: charset)
           addChar(c);
   }

    /**
     * Adds a character to the character set that is used for matching with images. If character already
     * exists in the character set, it does nothing.
     * @param c the character to add.
     */
   public void addChar(char c) {

       if(charsBrightness[c] == DEFAULT_IF_BRIGHTNESS_NOT_COMPUTED) {
           addToCharsAndAllCharsBrightness(c);
           boolean isMinUpdated = updateCharWithMinBrightness(c);
           boolean isMaxUpdated = updateCharWithMaxBrightness(c);
           if(!isMinUpdated && !isMaxUpdated) {
               double charNormalizedBrightness = normalizeBrightness(charsBrightness[c]);
               addToNormalizedBrightnessChars(charNormalizedBrightness, c);
           }
           reCreateCharsNormalizedBrightness();
       }
   }

    /**
     * Removes a character from the character set that is used for matching with images. If the character
     * doesn't exist in the character set, it does nothing.
     * @param c the character to remove.
     */
   public void removeChar(char c) {

       double cBrightness = charsBrightness[c];

       if(cBrightness != DEFAULT_IF_BRIGHTNESS_NOT_COMPUTED) {
           removeFromNormalizedBrightnessChars(c, cBrightness);

           charsBrightness[c] = DEFAULT_IF_BRIGHTNESS_NOT_COMPUTED;

           if((c == charWithMaxBrightness && findAndUpdateCharWithMaxBrightness()) ||
                   (c == charWithMinBrightness && findAndUpdateCharWithMinBrightness()))
               reCreateCharsNormalizedBrightness();
       }

   }

    /**
     * Gets the characters that are used for matching with images.
     * @return the characters that are used for matching with images.-
     */
   public char[] getCharsUsed() {
       int numOfChars = 0;
       for (double brightness : charsBrightness)
           if (brightness != DEFAULT_IF_BRIGHTNESS_NOT_COMPUTED)
               numOfChars += 1;

       char[] chars = new char[numOfChars];
        int pos = 0;
       for (char i = 0; i < charsBrightness.length; i++) {
           if(charsBrightness[i] != -1) {
               chars[pos] = i;
               pos += 1;
           }
       }
       return chars;
   }

    /**
     * Matches the character with the closest brightness to a given image brightness.
     * @param brightness brightness of the image.
     * @return the character that is with the closest brightness to the given brightness.
     */
   public char getCharByImageBrightness(double brightness) {
       double closestBrightness;
       Double closestFloorBrightness = normalizedBrightnessChars.floorKey(brightness);
       Double closestCeilingBrightness = normalizedBrightnessChars.ceilingKey(brightness);
       if(closestFloorBrightness == null)
           closestBrightness = closestCeilingBrightness;
       else if(closestCeilingBrightness == null)
           closestBrightness = closestFloorBrightness;
       else {
           closestBrightness = closestBrightnessBetweenFloorAndCeiling(
                   brightness,
                   closestFloorBrightness,
                   closestCeilingBrightness);
       }
       return normalizedBrightnessChars.get(closestBrightness).peek();
   }

   /*
    * Computes the brightness of a character.
    */
   private static double computeCharBrightness(char c) {
       boolean[][] charImg = CharConverter.convertToBoolArray(c);
       int numOfWhitePixels = countWhitePixelsInImg(charImg);
       int sizeOfImg = charImg.length * charImg[0].length;
       return (double) numOfWhitePixels / sizeOfImg;
   }

   /*
    * Counts the number of white pixels in an image.
    */
   private static int countWhitePixelsInImg(boolean[][] img) {
       int numOfWhitePixels = 0;
       for (int i = 0; i < img.length; i++) {
           for (int j = 0; j < img[i].length; j++) {
               if(img[i][j])
                   numOfWhitePixels += 1;
           }
       }
       return numOfWhitePixels;
   }

   /*
    * Adds a char's brightness to charsBrightness.
    */
   private void addToCharsAndAllCharsBrightness(char c) {
       if(allCharsBrightness[c] == -1) {
           allCharsBrightness[c] = computeCharBrightness(c);
       }
       charsBrightness[c] = allCharsBrightness[c];
   }

   /*
    * Removes a character from the normalized brightness characters. if after removing it, the priority
    * queue that is belonged to is empty, it removes the normalized brightness as well.
    */
   private void removeFromNormalizedBrightnessChars(char c, double cBrightness) {
       double cNormalizedBrightness = normalizeBrightness(cBrightness);
       normalizedBrightnessChars.get(cNormalizedBrightness).remove(c);
       //if priority queue empty, remove the normalized brightness.
       if(normalizedBrightnessChars.get(cNormalizedBrightness).isEmpty()){
           normalizedBrightnessChars.remove(cNormalizedBrightness);
       }
   }

   /*
    * Adds a character and it's normalized brightness to the normalizedBrightnessChars map.
    */
   private void addToNormalizedBrightnessChars(double normalizedBrightness, char c) {
       if(normalizedBrightnessChars.get(normalizedBrightness) == null) {
           PriorityQueue<Character> priorityQueue = new PriorityQueue<>();
           priorityQueue.add(c);
           normalizedBrightnessChars.put(normalizedBrightness, priorityQueue);
       }
       else
           normalizedBrightnessChars.get(normalizedBrightness).add(c);
   }

   /*
    * Computes new normalized brightnesses of the characters, and recreates the charsNormalizedBrightness map.
    */
   private void reCreateCharsNormalizedBrightness() {
       normalizedBrightnessChars.clear();
       for (char i = 0; i < charsBrightness.length; i++) {
           if(charsBrightness[i] != DEFAULT_IF_BRIGHTNESS_NOT_COMPUTED) {
               double charNormalizedBrightness = normalizeBrightness(charsBrightness[i]);
               addToNormalizedBrightnessChars(charNormalizedBrightness, i);
           }
       }
   }

   /*
    * Returns the closest brightness in absolute value out of two brightnesses to a given brightness.
    */
   private double closestBrightnessBetweenFloorAndCeiling(
           double brightness, double closestFloorBrightness, double closestCeilingBrightness) {
       if(Math.abs(brightness - closestFloorBrightness) < Math.abs(brightness - closestCeilingBrightness))
           return closestFloorBrightness;
       return closestCeilingBrightness;
   }

   /*
    * Finds the character that has the maximum brightness and updates the charWithMaxBrightness accordingly.
    */
   private boolean findAndUpdateCharWithMaxBrightness() {
       char newCharWithMaxBrightness = (char) 0;
       for (char i = 0; i < charsBrightness.length; i++) {
           if (charsBrightness[i] > charsBrightness[newCharWithMaxBrightness])
               newCharWithMaxBrightness = i;
       }

       if(newCharWithMaxBrightness != charWithMaxBrightness) {
           charWithMaxBrightness = newCharWithMaxBrightness;
           return true;
       }
       return false;
   }

   /*
    * Finds the character that has the minimum brightness and updates the charWithMinBrightness accordingly.
    */
   private boolean findAndUpdateCharWithMinBrightness() {
       char newCharWithMinBrightness = (char) 0;
       for (char i = 0; i < charsBrightness.length; i++) {
           if(charsBrightness[i] != -1 &&
                   (charsBrightness[newCharWithMinBrightness] == -1 ||
                           charsBrightness[i] < charsBrightness[newCharWithMinBrightness]))
               newCharWithMinBrightness = i;
       }

       if(newCharWithMinBrightness != charWithMinBrightness) {
           charWithMinBrightness = newCharWithMinBrightness;
           return true;
       }
       return false;
   }

   /*
    * Updates the character with the minimum brightness if c has a smaller brightness that the brightness
    * of charWithMinBrightness. returns true if succeeded and false otherwise.
    */
   private boolean updateCharWithMinBrightness(char c) {
       if(charsBrightness[charWithMinBrightness] == -1. ||
               charsBrightness[c] < charsBrightness[charWithMinBrightness]) {
           charWithMinBrightness = c;
           return true;
       }
       return false;
   }

    /*
     * Updates the character with the maximum brightness if c has a smaller brightness that the brightness
     * of charWithMaxBrightness. returns true if succeeded and false otherwise.
     */
   private boolean updateCharWithMaxBrightness(char c) {
       if(charsBrightness[c] > charsBrightness[charWithMaxBrightness]) {
           charWithMaxBrightness = c;
           return true;
       }
       return false;
   }

   /*
    * Computes and returns normalized brightness of a given brightness.
    */
   private double normalizeBrightness(double brightness) {
       return (brightness - charsBrightness[charWithMinBrightness]) /
               (charsBrightness[charWithMaxBrightness] - charsBrightness[charWithMinBrightness]);
   }
}