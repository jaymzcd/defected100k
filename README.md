# Defected 100k

Generate a giant image (or set of individual rows/tiles) based on a source
folder and a mask image to control a transform based on pixels values in some
way.

This presently simply uses the average brightness of a pixel to classify tiles
as either dark or bright and enhances them accordingly before outputting them
into an individual row.

The resultant rows can then be merged together using montage with imagemagick
memory permitting. Alternatively output smaller slices and combine these in
two dimensions to create tiles of a more manageable size.

Images which can't be processed at the time are skipped over and logged to
console. The choice of 317 images per row is related to this being developed
for a particular case whereby the grid was to fit 100,000 items - 317**2 =
100,489.

## Montaging together the rows

The reason I didn't use montage to do each row to begin with was that the test
output had some shifting in it further down the line. I'm not sure if 'magick
is designed to reliably handle tens of thousands of pixels - it could also have
been some issue with an input image. Regardless when the images were combined
using PIL the output was as expected first time.

Stitching the rows together though is easy to accomplish with imagemagick and
can be done in batches to further ease the requirements:

    DIG=11
    montage row_${DIG}*.png -tile 1x -geometry +0+0 out_$dig_0-9.png;

This would create a full-scale combined image of `row_110.png` - `row_119.png`.

## Tile Cutting

### Attempt 1

A GPL script to generate tiles at zoom levels can be found
[on Google Code](https://code.google.com/p/googletilecutter/). This generates
various zoom levels in the form z{Z}x{X}y{Y}.png. The map.html file then loads
these in as a maps application. This code is pretty much verbatim from the demo
on the [Google site](https://developers.google.com/maps/documentation/javascript/maptypes#ImageMapTypes).

### Attempt 2

Using [MapTiler](http://www.maptiler.org/)
