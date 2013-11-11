#!/usr/bin/env python2

import argparse
import os
from glob import iglob
from PIL import Image, ImageEnhance


def read_mask(mask_path):
    """
        Read a souce image mask and return the pixel data for it
    """
    mask = Image.open(mask_path)
    pixels = list(mask.getdata())
    width, height = mask.size
    pixels = [pixels[i * width:(i + 1) * width] for i in xrange(height)]
    return pixels


def score(pixel):
    """
        Returns what will be used to tint the source image to give a representation
        of the contrast of the source mask. Takes a pixel which is a 4-tuple
        of rgbA. We will use this value as an alpha for the tile.
    """

    # Simply average the complete channel (this includes alpha!)
    score = sum(pixel)/len(pixel)

    # We don't want to completely obliterate blacks and darker colors so if we
    # have a low-ish score add an offset to it
    dark_offset = 50
    score = score + dark_offset if score < dark_offset else score

    return score


def generate(tiles, mask):
    """
        Generate a giant tiled image to certain specs
    """
    # each image will be 48px square - why that size? because some images were
    # saved out at that resolution (anything ending *normal without extension)
    # giving a total image size of a fairly manageable 15,216px square
    pixels = read_mask(mask)
    tiles = iglob(tiles)


    # We use 317 as 317^2 = 100489 which is the smallest square integer
    # that fits 100,000 'pixels'. A pixel in this case will be a twitter profile
    # Each tile is 48x48 (hardcodes - could get from first tile when looped)
    per_side = 317
    tile_size = (48, 48)

    try:
        os.mkdir('tiles')
    except OSError:
        pass


    def _get_tile():
        """
            Repeatedly try and return a valid PIL image
        """

        tile = tiles.next()
        try:
            return Image.open(tile)
        except IOError:
            print "[Skipping] Error opening %s" % tile
            return _get_tile()

    for row_num, row in enumerate(pixels):
        row_image = Image.new('RGB', (tile_size[0] * per_side, tile_size[1]))

        if row_num < 105:
            continue

        for num, pixel in enumerate(row):

            tile_score = score(pixel)
            src_tile = _get_tile()

            if tile_score > 128:
                # For 'white' tiles use a bright version
                image = ImageEnhance.Brightness(src_tile).enhance(1.33)
            else:
                # For dark tiles use a darkened version
                image = ImageEnhance.Brightness(src_tile).enhance(0.37)
                # If we have dark tiles use black and white version
                # image = src_tile.convert('L')

            # note we are only shifting across! each row is output individually
            # rather than one giant image
            row_image.paste(image, (num * tile_size[0], 0))

        image_name = 'tiles/row_%03d.png' % row_num
        row_image.save(image_name)
        print image_name


if __name__ == '__main__':
    # Set our defaults for this project
    avatar_path = 'avatars/*'
    mask_path = 'assets/317.png'

    # Simple argument parser to handle things a bit more flexibly than sys.argv
    parser = argparse.ArgumentParser(description='Generate giant image from source based on a mask')
    parser.add_argument('-t', '--tiles', dest='tiles', action='store', default=avatar_path,
        help='Path to images for use as tiles')
    parser.add_argument('-m', '--mask', dest='mask', action='store', default=mask_path,
       help='Path to source image for mask')
    args = parser.parse_args()

    # Lets do it!
    generate(args.tiles, args.mask)
