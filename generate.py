#!/usr/bin/env python2

import argparse
import os
import MySQLdb as mdb

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


def generate(tiles, mask, offset):
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

    sql_script = open('map/coords.sql', 'w')
    con = mdb.connect('localhost', 'root', os.environ['DBPASS'], 'def100k');
    cur = con.cursor()

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
            i = Image.open(tile)

            # If the image is indexed then when PIL converts to RGB (for brightness)
            # a bug means it'll return an all white image. This is recent (like 09/13)
            # http://stackoverflow.com/questions/19892919/pil-converting-an-image-with-mode-i-to-rgb-results-in-a-fully-white-image
            # So lets log that for now and move on with a new image

            mode = i.mode
            if mode != 'I':
                return i, tile
            else:
                print "[Skipping] IndexedMode: %s" % tile
                return _get_tile()

        except IOError:
            print "[Skipping] IOError: %s" % tile
            return _get_tile()

    for row_num, row in enumerate(pixels):
        row_image = Image.new('RGB', (tile_size[0] * per_side, tile_size[1]))

        for num, pixel in enumerate(row):

            ypos = row_num + offset

            tile_score = score(pixel)
            src_tile, src_name = _get_tile()

            if tile_score > 128:
                # For 'white' tiles use a bright version
                try:
                    image = ImageEnhance.Brightness(src_tile).enhance(1.33)
                except ValueError:
                    # Might get a conversion error, skip for now and use as is
                    image = src_tile
            else:
                # For dark tiles use a darkened version
                try:
                    image = ImageEnhance.Brightness(src_tile).enhance(0.37)
                except ValueError:
                    image = src_tile
                # If we have dark tiles use black and white version
                # image = src_tile.convert('L')

            # TODO: HACK!!
            filename = src_name.replace('avatars/batch1/', '')
            filename = src_name.replace('avatars/batch2/', '')

            # note we are only shifting across! each row is output individually
            # rather than one giant image
            row_image.paste(image, (num * tile_size[0], 0))
            # Store the tile location for this so we can look it up and add a marker
            # easily on the finished map. Note there's
            stmt = """
                UPDATE images SET xpos=%d, ypos=%d WHERE filename="%s";
            """ % (num, ypos, filename)

            sql_script.write(stmt)
            cur.execute(stmt)
            con.commit()
            print stmt

        image_name = 'tiles/row_%03d.png' % ypos
        row_image.save(image_name)

        print "Output %s" % image_name

    sql_script.close()
    con.close()


if __name__ == '__main__':
    # Set our defaults for this project
    avatar_path = 'avatars/batch1'
    mask_path = 'assets/317.png'

    # Simple argument parser to handle things a bit more flexibly than sys.argv
    parser = argparse.ArgumentParser(description='Generate giant image from source based on a mask')
    parser.add_argument('-t', '--tiles', dest='tiles', action='store', default=avatar_path,
        help='Path to images for use as tiles')
    parser.add_argument('-m', '--mask', dest='mask', action='store', default=mask_path,
       help='Path to source image for mask')
    parser.add_argument('-o', '--offset', dest='offset', action='store', type=int, default=0,
       help='Offset for the row positions - use this to import new rows with correct tile coords on the map')
    args = parser.parse_args()

    # Lets do it!
    generate('%s/*' % args.tiles, args.mask, args.offset)
