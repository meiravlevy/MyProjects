package ascii_art;


import image.Image;
import image.ImageProcessor;
import image_char_matching.SubImgCharMatcher;
import java.util.ArrayList;

/**
 * Class in charge of running the asciiArt algorithm.
 */
public class AsciiArtAlgorithm {
    private final SubImgCharMatcher subImgCharMatcher;
    private final ArrayList<Image> subImages;
    private final int imageResolution;

    /**
     * constructor.
     * @param subImgCharMatcher matches between characters and images according to their brightness.
     * @param subImages sub images of a full image that we want to do the ascii art for.
     * @param imageResolution the resolution of the full image.
     */
    public AsciiArtAlgorithm(SubImgCharMatcher subImgCharMatcher, ArrayList<Image> subImages,
                             int imageResolution) {
        this.subImgCharMatcher = subImgCharMatcher;
        this.subImages = subImages;
        this.imageResolution = imageResolution;

    }

    /**
     * runs the AsciiArt algorithm.
     * @return a 2d array of characters that were replaced with the sub images.
     */
    public char[][] run(){
        char[][] imageInChars = new char[subImages.size() / imageResolution][imageResolution];

        for (int row = 0; row < imageInChars.length; row++)
            for (int col = 0; col < imageInChars[row].length; col++) {
                double subImgBrightness =
                        ImageProcessor.computeBrightness(subImages.get(row * imageResolution + col));
                imageInChars[row][col] = subImgCharMatcher.getCharByImageBrightness(subImgBrightness);
            }
        return imageInChars;
    }
}
