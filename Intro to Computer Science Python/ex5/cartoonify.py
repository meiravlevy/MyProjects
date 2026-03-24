#################################################################
# FILE : cartoonify.py
# WRITER : Meirav Levy , meiravlevy
# EXERCISE : intro2cs2 ex5 2021
# DESCRIPTION: A simple program that cartoonifies an image
# STUDENTS I DISCUSSED THE EXERCISE WITH:
# WEB PAGES I USED: stack overFlow, youtube.
# NOTES: ...
#################################################################

from ex5_helper import *
import math
import sys


def make_one_color_pixel(image, row, color_ind, num_of_col):
    """
    Goes over the pixels in the row and creates a new pixel containing
    shades of the same color.
    :param image: a 3D list containing pixels of different colors
    :param row: A number of a row in the image
    :param color_ind: The index of the color that we want to make an image from
    :param num_of_col: The number of pixels in the row
    :return: One pixel that contains shades of the same color.
    """
    pixel = [image[row][col][color_ind] for col in range(num_of_col)]
    return pixel


def make_one_color_image(image, color_ind):
    """
    Iterates over the all the pixels in the image and creates a new image
    with shades of the same color.
    :param image: a 3D list containing pixels of different colors
    :param color_ind: The index of the color that we want to make an image from
    image from
    :return: An image with only one color- the color given to the function.
    """
    num_of_rows = len(image)
    num_of_col = len(image[0])
    color_image = [make_one_color_pixel(image, row, color_ind, num_of_col)
                   for row in range(num_of_rows)]
    return color_image


def separate_channels(image):
    """
    Goes over all the colors in the image and creates a new list containing
    2D images, Each image in the list is in shades of the same color.
    :param image: a 3D list containing pixels of in different colors
    :return: a 3D list containing 2D lists of pictures with the same color
    """
    pixel_len = len(image[0][0])
    same_color_pictures = [make_one_color_image(image, color) for color
                           in range(pixel_len)]
    return same_color_pictures


def make_dif_color_pixel(channels, col, shade):
    """
    :param channels: a 3D list with 2D images, each in one color only.
    :param col: the number of pixels in each 2D image.
    :param shade: the shade of the color in a pixel.
    :return: a pixel with all the colors in the channels list.
    """
    num_of_colors = len(channels)
    pixel_of_dif_color = [channels[color][col][shade] for color
                          in range(num_of_colors)]
    return pixel_of_dif_color


def make_dif_color_row(channels, col):
    """
    :param channels: a 3D list with 2D images, each in one color only.
    :param col: the number of pixels in each 2D image.
    :return: a row with pixels in all colors that are in channels list.
    """
    num_of_shades = len(channels[0][0])
    row_of_dif_color_pixel = [make_dif_color_pixel(channels, col, shade) for
                              shade in range(num_of_shades)]
    return row_of_dif_color_pixel


def combine_channels(channels):
    """
    :param channels: a 3D list with 2D images, each in one color only.
    :return: A new image in all colors that are in channels list.
    """
    num_of_pixels = len(channels[0])
    dif_color_image = [make_dif_color_row(channels, col) for col
                       in range(num_of_pixels)]
    return dif_color_image


def make_grayscale_pixel(pixel):
    """
    :param pixel: a pixel in a row of the colored image.
    :return: a grayscale pixel
    """
    gray_scale = 0
    for color in range(3):
        if color == 0:
            gray_scale += pixel[color] * 0.299  # For red color
        elif color == 1:
            gray_scale += pixel[color] * 0.587  # For green color
        elif color == 2:
            gray_scale += pixel[color] * 0.114  # For blue color
    gray_scale_pixel = round(gray_scale)
    return gray_scale_pixel


def make_grayscale_row(row):
    """
    :param row: a row in the colored image
    :return: a row in grayscale
    """
    row_grayscale = [make_grayscale_pixel(pixel) for pixel in row]
    return row_grayscale


def RGB2grayscale(colored_image):
    """
    :param colored_image: a 3D list that we want to turn to grayscale.
    :return: a new image in grayscale.
    """
    gray_scale_image = [make_grayscale_row(row)
                        for row in colored_image]
    return gray_scale_image


def blur_kernel(size):
    """
    Will create a (size x size) kernel and each value will be 1 / size**2
    """
    kernel_cells_size = 1 / size**2
    kernel = [[kernel_cells_size] * size] * size
    return kernel

def initialize_image(height, width, value=0):
    """This function initializes an image with height as the number of rows
    and width as the number of pixels, and the value of each pixel is 0"""
    new_image = []
    for height in range(height):
        row = [value] * width
        new_image.append(row)
    return new_image


def is_index_in_list(list, ind):
    """This function checks if an index is valid in the list given"""
    if 0 <= ind < len(list):
        return True
    return False


def add_same_value_to_list(pixel_value, pixel_nbrs, size_side_kernel):
    """This function will append the same value to the list <size_side_kernel>
    times"""
    for num in range(size_side_kernel):
        pixel_nbrs.append(pixel_value)
    return pixel_nbrs


def get_pixel_nbrs(image, ind_row, ind_pixel, size_side_kernel):
    """This function checks who are the neighbours of a pixel in the image
    and returns a new list containing those values, and if the pixel doesn't
    have enough neighbours, this list will add the value of that pixel."""
    nbrs_expected_num = int((size_side_kernel - 1) / 2)
    default_pixel = image[ind_row][ind_pixel]
    pixel_nbrs = []
    for index_row in range(ind_row - nbrs_expected_num, ind_row + nbrs_expected_num + 1):
        if not is_index_in_list(image, index_row):
            pixel_nbrs = add_same_value_to_list(default_pixel, pixel_nbrs, size_side_kernel)
            continue
        for index_col in range(ind_pixel - nbrs_expected_num, ind_pixel + nbrs_expected_num + 1):
            if is_index_in_list(image[index_row], index_col):
                pixel_nbrs.append(image[index_row][index_col])
            else:
                pixel_nbrs.append(default_pixel)
    return pixel_nbrs


def calc_kernel_on_pixel(kernel, pixel_nbrs):
    """This function calculates the pixel's value after applying a kernel
    over it."""
    sum = 0
    ind_pixel_nbrs = 0
    for ind_row in range(len(kernel)):
        for ind_pixel in range(len(kernel)):
            sum += kernel[ind_row][ind_pixel] * pixel_nbrs[ind_pixel_nbrs]
            ind_pixel_nbrs += 1
    if sum > 255:
        return 255
    elif sum < 0:
        return 0
    return round(sum)


def apply_kernel(image, kernel):
    size_side_kernel = len(kernel)
    applied_kernel_image = initialize_image(len(image), len(image[0]))
    for ind_row in range(len(image)):
        for ind_pixel in range(len(image[0])):
            pixel_nbrs = get_pixel_nbrs(image, ind_row, ind_pixel,
                                        size_side_kernel)
            applied_kernel_image[ind_row][ind_pixel] = \
                calc_kernel_on_pixel(kernel, pixel_nbrs)
    return applied_kernel_image


def relative_part_of_num(num):
    """This function takes a number between 0 and 1 and returns both the number
    and the complementary of the number to 1"""
    if num <= 0.5:
        bigger_relative_part = 1 - num
        smaller_relative_part = num
        return bigger_relative_part, smaller_relative_part
    else:
        smaller_relative_part = 1 - num
        bigger_relative_part = num
    return smaller_relative_part, bigger_relative_part


def make_num_between_0_and_1(num):
    """This function takes a number and returns the number after the decimal
    point if the number isn't an integer, and if the number is an integer, it
    it will return either 1 or 0"""
    num = float(num)
    if num.is_integer() and num >= 1:
        return num - (num - 1)
    return num % 1


def is_coord_on_limit(coord):
    """This function takes a coordination and checks if it is in the limits of
    the picture, meaning it is an integer"""
    coord = float(coord)
    if coord.is_integer():
        return True
    return False


def bilinear_interpolation(image, y, x):
    """
    The function will check where the pixel should be exactly and calculate
    it's value by using the pixels that it is close too in the image.
    :param image: a 2D list with one color only
    :param y: the length coordination of the pixel
    :param x: the width coordination of the pixel
    :return: The value of the pixel
    """

    # In this function we will use:
    # a - as the top left corner
    # b - as the bottom left corner
    # c - as the top right corner
    # d - as the bottom right corner

    x_betw_0_and_1 = make_num_between_0_and_1(x)
    y_betw_0_and_1 = make_num_between_0_and_1(y)
    ac_relative_part_of_y, bd_relative_part_of_y = \
        relative_part_of_num(y_betw_0_and_1)
    ab_relative_part_of_x, cd_relative_part_of_x = \
        relative_part_of_num(x_betw_0_and_1)
    if is_coord_on_limit(x):
        a = image[math.floor(y)][int(x)]
        b = image[math.ceil(y)][int(x)]
        return round(a*ac_relative_part_of_y + b*bd_relative_part_of_y)
    if is_coord_on_limit(y):
        b = image[int(y)][math.floor(x)]
        d = image[int(y)][math.ceil(x)]
        return round(b*ab_relative_part_of_x + d*cd_relative_part_of_x)
    a = image[math.floor(y)][math.floor(x)]
    b = image[math.ceil(y)][math.floor(x)]
    c = image[math.floor(y)][math.ceil(x)]
    d = image[math.ceil(y)][math.ceil(x)]
    return round(a*ab_relative_part_of_x*ac_relative_part_of_y +
                 b*ab_relative_part_of_x*bd_relative_part_of_y +
                 c*cd_relative_part_of_x*ac_relative_part_of_y +
                 d*cd_relative_part_of_x*bd_relative_part_of_y)


def resize(image, new_height, new_width):
    """
    :param image: The original image that we want to resize
    :param new_height: the height of the new image
    :param new_width: the width of the new image
    :return: A new image resized (bigger or smaller than the original)
    """
    new_image = initialize_image(new_height, new_width)
    original_height = len(image)
    original_width = len(image[0])
    y_original_coord_scale = (original_height - 1) / (new_height - 1)
    x_original_coord_scale = (original_width - 1) / (new_width - 1)
    for row in range(new_height):
        original_y_coord = y_original_coord_scale * row
        for col in range(new_width):
            original_x_coord = x_original_coord_scale * col
            new_image[row][col] = bilinear_interpolation(image,
                                                         original_y_coord,
                                                         original_x_coord)
    return new_image


def r_turn_col_to_row(image, col):
    """This function takes a column in the image and turns it into a row
    to the right"""
    num_of_rows = len(image)
    new_row = [image[row][col] for row in range(num_of_rows - 1, -1, -1)]
    return new_row


def l_turn_col_to_row(image, col):
    """This function takes a column in the image and turns it into a row to
    the left"""
    num_of_rows = len(image)
    new_row = [image[row][col] for row in range(num_of_rows)]
    return new_row


def rotate_90(image, direction):
    """
    :param image: The image that we want to rotate.
    :param direction: R - rotate to the right, L- rotate to the left.
    :return: the rotated image
    """
    num_of_col = len(image[0])
    if direction == "R":
        rotated_image_r = [r_turn_col_to_row(image, col) for
                           col in range(num_of_col)]
        return rotated_image_r
    rotated_image_l = [l_turn_col_to_row(image, col) for
                       col in range(num_of_col - 1, -1, -1)]
    return rotated_image_l


def get_edges(image, blur_size, block_size, c):
    image_with_edges = []
    kernel = blur_kernel(blur_size)
    blurred_image = apply_kernel(image, kernel)
    for ind_row in range(len(blurred_image)):
        image_with_edges.append([])
        for ind_pixel in range(len(blurred_image[0])):
            pixel_nbrs = get_pixel_nbrs(blurred_image, ind_row, ind_pixel,
                                        block_size)
            threshold_pixel = sum(pixel_nbrs) / len(pixel_nbrs)
            if blurred_image[ind_row][ind_pixel] < (threshold_pixel - c):
                image_with_edges[ind_row].append(0)
            else:
                image_with_edges[ind_row].append(255)
    return image_with_edges


def quantize_pixel(pixel, N):
    """
    :param pixel: the pixel we want to quantize.
    :param N: the number of shades of colors.
    :return: the new shade of the pixel.
    """
    quantized_pixel = round(math.floor(pixel * N/255) * 255/N)
    return quantized_pixel


def quantize(image, N):
    """This function changes the values of all the pixels to be quantized."""
    num_of_rows = len(image)
    num_of_col = len(image[0])
    quantized_image = [[quantize_pixel(image[row][col], N) for col
                        in range(num_of_col)] for row in range(num_of_rows)]
    return quantized_image


def quantize_colored_image(image, N):
    """This function will quantize a colored image."""
    separated_channels = separate_channels(image)
    quantized_channels = [quantize(separated_channels[color], N) for
                          color in range(len(separated_channels))]
    quantized_colored_image = combine_channels(quantized_channels)
    return quantized_colored_image


def calculate_mask(pixel1, pixel2, mask_pixel):
    """This function calculates the value of a new pixel masked"""
    return round(pixel1 * mask_pixel +
                 pixel2 * (1 - mask_pixel))


def add_mask(image1, image2, mask):
    """This function takes 2 images in the same dimensions and a mask and
    returns a new image masked."""
    num_of_rows = len(image1)
    num_of_pixels = len(image1[0])
    if type(image1[0][0]) == int:
        image_with_mask = [[calculate_mask(image1[row][pixel],
                          image2[row][pixel], mask[row][pixel])for
                            pixel in range(num_of_pixels)] for row
                           in range(num_of_rows)]
        return image_with_mask
    else:
        image_with_mask = []
        num_of_colors = len(image1[0][0])
        for row in range(num_of_rows):
            new_row = []
            for pixel in range(num_of_pixels):
                new_pixel = []
                for color in range(num_of_colors):
                    new_pixel.append(calculate_mask(image1[row][pixel][color],
                                                    image2[row][pixel][color],
                                                    mask[row][pixel]))
                new_row.append(new_pixel)
            image_with_mask.append(new_row)
        return image_with_mask


def create_mask_image(gray_scale_image):
    """takes an image in one color and creates a mask for it."""
    masked_image = [[gray_scale_image[ind_row][ind_pixel] / 255 for ind_pixel
                     in range(len(gray_scale_image[0]))] for ind_row in
                    range(len(gray_scale_image))]
    return masked_image


def cartoonify(image, blur_size, th_block_size, th_c, quant_num_shades):
    """cartoons an image"""
    gray_scale_image = RGB2grayscale(image)
    image_with_edges = get_edges(gray_scale_image, blur_size,
                                 th_block_size, th_c) # 2D
    mask = apply_kernel(image_with_edges, [[1/255]])
    quantized_image = quantize_colored_image(image, quant_num_shades)
    separated_channels = separate_channels(quantized_image) #2D
    for ind_channel in range(len(separated_channels)):
        separated_channels[ind_channel] = add_mask(
            separated_channels[ind_channel], image_with_edges, mask)
    colored_image_with_mask = combine_channels(separated_channels)
    return colored_image_with_mask


if __name__ == '__main__':
    image = load_image("C:\pycharm\year1\ex5\ziggy.jpg")
    if len(sys.argv) != 8:
        print("wrong number of arguments")
    image_source = sys.argv[1]
    cartoon_dest = sys.argv[2]
    max_im_size = int(sys.argv[3])
    blur_size = int(sys.argv[4])
    th_block_size = int(sys.argv[5])
    th_c = float(sys.argv[6])
    quant_num_shades = int(sys.argv[7])
    image = load_image(image_source)
    height = len(image)
    width = len(image[0])
    separated_channels = separate_channels(image)
    if height > width and height > max_im_size:
        for ind_channel in range(len(separated_channels)):
            separated_channels[ind_channel] = resize(
                separated_channels[ind_channel], max_im_size,
                               round(width / (height / max_im_size)))
        combined_channels = combine_channels(separated_channels)
    elif width > max_im_size:
        for ind_channel in range(len(separated_channels)):
            separated_channels[ind_channel] = resize(
                separated_channels[ind_channel],
                round(height / (width / max_im_size)), max_im_size)
        combined_channels = combine_channels(separated_channels)
    else:
        combined_channels = image
    cartooned_image = cartoonify(combined_channels, blur_size, th_block_size,
                                     th_c, quant_num_shades)
    save_image(cartooned_image, cartoon_dest)

