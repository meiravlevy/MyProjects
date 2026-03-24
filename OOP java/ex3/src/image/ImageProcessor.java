package image;

import java.awt.*;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedList;

/**
 * A class that contains methods for performing different operations on an image.
 * @author Meirav Levy
 */
public class ImageProcessor {
    private static final int MAX_RGB_SCORE = 255;

    /**
     * Constructor.
     */
    public ImageProcessor() {}

    /**
     * Pads an image with white pixels so that the width and height of the image will be in the power of 2.
     * @param imageToProcess - The image we want to pad.
     * @return The padded image while the padding is symmetrical in the sides of the image.
     */
    public static Image padImage(Image imageToProcess) {
        int numOfPixelsToAddToWidth = computeNumOfPixelsToPadDimension(imageToProcess.getWidth());
        int numOfPixelsToAddToHeight = computeNumOfPixelsToPadDimension(imageToProcess.getHeight());
        int width = imageToProcess.getWidth() + numOfPixelsToAddToWidth;
        int height = imageToProcess.getHeight() + numOfPixelsToAddToHeight;

        Color[][] pixelArray = makePaddedPixelArray(
                imageToProcess, numOfPixelsToAddToWidth, numOfPixelsToAddToHeight);
        return new Image(pixelArray, width, height);
    }

    /**
     * Creates a padded image and divides it to square subImages.
     * @param imageToProcess the image to process.
     * @param resolution the number of sub images in a row.
     * @return the sub images of the padded image by order.
     */
    public static ArrayList<Image> divideImageToSubImages(Image imageToProcess, int resolution) {
        Image paddedImage = padImage(imageToProcess);
        int squareSideLength = paddedImage.getWidth() / resolution;
        ArrayList<Image> subImages = new ArrayList<>();
        for(int row = 0; row < paddedImage.getHeight(); row += squareSideLength) {
            for(int col = 0; col < paddedImage.getWidth(); col += squareSideLength) {
                Color[][] subPixelArray = createSubPixelArray(paddedImage, squareSideLength, row, col);
                Image subImage = new Image(subPixelArray, squareSideLength, squareSideLength);
                subImages.add(subImage);
            }
        }
        return subImages;
    }

    /**
     * Computes the brightness of an image.
     * @param imageToProcess the image to compute brightness for.
     * @return the brightness of the image.
     */
    public static double computeBrightness(Image imageToProcess) {
        double sumGreyPixels = 0;
        for (int row = 0; row < imageToProcess.getHeight(); row++) {
            for (int col = 0; col < imageToProcess.getWidth(); col++) {
                Color color = imageToProcess.getPixel(row, col);
                sumGreyPixels += convertPixelToGrey(color);
            }
        }
        return sumGreyPixels / (imageToProcess.getHeight() * imageToProcess.getWidth() * MAX_RGB_SCORE);
    }
    /*
     * Computes the number of pixels needed for padding onw of the dimension of an image.
     */
    private static int computeNumOfPixelsToPadDimension(int dim) {
        int pixelsToPadWidth = 0;
        while (!isNumPowerOfTwo(dim + pixelsToPadWidth)) {
            pixelsToPadWidth += 2;
        }
        return pixelsToPadWidth;
    }

    /*
     * Converts the color of a pixel to grey.
    */
    private static double convertPixelToGrey(Color color) {
        return color.getRed() * 0.2126 + color.getGreen() * 0.7152 + color.getBlue() * 0.0722;
    }

    /*
     * Creates a sub pixel array where the top left corner is in the row and col given as arguments.
     */
    private static Color[][] createSubPixelArray(Image paddedImage, int arrLength, int row, int col) {
        Color[][] subPixelArray = new Color[arrLength][arrLength];
        for(int x = 0; x < arrLength; x++){
            for(int y = 0; y < arrLength; y++) {
                subPixelArray[x][y] = paddedImage.getPixel(row + x, col + y);
            }
        }
        return subPixelArray;
    }



    /*
     * check if a number is the power of two. return true if it is and false otherwise.
     */
    private static boolean isNumPowerOfTwo(int num) {
        while((num % 2) == 0) {
            num = num / 2;
        }
        return num == 1;
    }

    /*
     * pads the pixel array of the given image with white pixels.
     */
    private static Color[][] makePaddedPixelArray(
            Image imageToPad, int numOfPixelsToAddToWidth, int numOfPixelsToAddToHeight) {
        Color[][] pixelArray =
                new Color[imageToPad.getHeight() + numOfPixelsToAddToHeight]
                        [imageToPad.getWidth() + numOfPixelsToAddToWidth];

        //pad top of image
        padHeightOfImage(0, numOfPixelsToAddToHeight, pixelArray);

        //pad bottom of image
        padHeightOfImage(
                imageToPad.getHeight() + numOfPixelsToAddToHeight / 2,
                pixelArray.length, pixelArray);

        //pad left side of image
        padWidthOfImage(0, numOfPixelsToAddToWidth/2, pixelArray);

        padWidthOfImage(imageToPad.getWidth() + numOfPixelsToAddToWidth / 2,
                pixelArray[0].length, pixelArray);

        fillPaddedImageWithImagePixels(
                imageToPad, numOfPixelsToAddToHeight/2,
                numOfPixelsToAddToWidth/2, pixelArray);
        return pixelArray;
    }

    /*
     * pads the height of the pixel array of an image with white pixels.
     */
    private static void padHeightOfImage(int rowStartPos, int rowEndPos, Color[][]pixelArray) {
        for (int i = rowStartPos; i < rowEndPos; i++)
            Arrays.fill(pixelArray[i], Color.WHITE);
    }

    /*
     * pads the width of the pixel array of an image with white pixels.
     */
    private static void padWidthOfImage(int colStartPos, int colEndPos, Color[][] pixelArray) {
        for(int i = 0; i < pixelArray.length; i++) {
            for(int j = colStartPos; j < colEndPos; j++) {
                pixelArray[i][j] = Color.WHITE;
            }
        }
    }

    /*
     * fills the padded image pixel array with the pixel array of the original image in the correct position.
     */
    private static void fillPaddedImageWithImagePixels(
            Image image, int heightPaddedPixels, int widthPaddedPixels, Color[][] pixelArray) {
        for(int i = 0; i < image.getHeight(); i++){
            for(int j = 0; j < image.getWidth(); j++) {
                pixelArray[heightPaddedPixels + i][widthPaddedPixels + j] = image.getPixel(i, j);
            }
        }
    }
}
