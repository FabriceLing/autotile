import argparse
import json
from enum import Enum
from PIL import Image

class TilesType(Enum):
    EMPTY = 0
    VERTICAL = 1
    HORIZONTAL = 2
    CROSS = 3
    FULL = 4

class TilesCorner(Enum):
    NORTHEAST = 0
    SOUTHEAST = 1
    SOUTHWEST = 2
    NORTHWEST = 3

def swap_bits(value, start_bit, end_bit):
    "Swaps two bits in a number"
    # Get the new value from the orignial without the two bits we are swapping.
    new_value = value & ~( 2 ** start_bit + 2 ** end_bit)

    # If start bit is on, set the end bit.
    if value & (2 ** start_bit):
        new_value += (2 ** end_bit)
    # If end bit is on, set the start bit.
    if value & (2 ** end_bit):
        new_value += (2 ** start_bit)

    # Return the new value.
    return new_value

def get_mask_for_tile(tile, corner):
    """Return the mask for the tile according to which corner is chosen.
        NORTHEAST is defined by bits 0, 1 and 2
        SOUTHEAST is defined by bits 2, 3 and 4
        SOUTHWEST is defined by bits 4, 5 and 6
        NORTHWEST is defined by bits 6, 7 and 1
        The mask is transformed so:
            bit 0 is vertical
            bit 1 is horizontal
            bit 2 is the corner
    """
    # Get bits 0, 1 and 2 for NORTHEAST corner.
    if corner == TilesCorner.NORTHEAST:
        tile = tile & 7
    # Get bits 2, 3 and 4 for SOUTHEAST corner.
    elif corner == TilesCorner.SOUTHEAST:
        tile = ( tile & 28 ) >> 2
        tile = swap_bits(tile, 0, 2)
    # Get bits 4, 5 and 6 for SOUTHWEST corner.
    elif corner == TilesCorner.SOUTHWEST:
        tile = ( tile & 112 ) >> 4 
    # Get bits 1, 6 and 7 for NORTHWEST corner.
    elif corner == TilesCorner.NORTHWEST:
        tile = (( tile & 192 ) >> 6) + (( tile & 1 ) << 2 )
        tile = swap_bits(tile, 0, 2)

    # Swap bits 1 and 2
    tile = swap_bits(tile, 1, 2)

    return tile

def get_tile_type(tile, corner):
    """Returns the Type of tile for this corner accoring to the current tile and the corner selected"""
    # Get the mask for this tile.
    mask = get_mask_for_tile(tile, corner)

    # If the corner is active, it's a full corner.
    if mask & 4:
        return TilesType.FULL
    else:
        return TilesType(mask)

def get_template_crop(template_image, tile, corner):
    """Get the sub-section of the template image for the current tile and corner"""
    # Get the tile from the type and corner.
    mask = get_tile_type(tile, corner)

    # Get default position.
    x_pos = mask.value * template_image.size[1]
    y_pos = 0

    # Offset the image in the appropriate corner.
    if corner == TilesCorner.NORTHEAST:
        x_pos += template_image.size[1] / 2
    elif corner == TilesCorner.SOUTHEAST:
        x_pos += template_image.size[1] / 2
        y_pos += template_image.size[1] / 2
    elif corner == TilesCorner.SOUTHWEST:
        y_pos += template_image.size[1] / 2

    # Return the sub-section of the template containing the image we need.
    return template_image.crop((x_pos, y_pos, x_pos + template_image.size[1] / 2, y_pos + template_image.size[1] / 2))

def open_template(filename):
    """Open the template file"""
    try:
        source = Image.open(filename)
    except (FileNotFoundError, OSError, SystemError) as err:
        print("Unable to load image '%s'" % filename)
        print("Error := %s" % err)
        return
    except:
        print("Unable to load image: '%s'" % filename)
        return
    return source

def generate_autotiles(template_filename, output_filename, width, height, array):
    """Generate the autotile from the template and layout information"""
    template_image = open_template(template_filename)
    if template_image == None:
        return
    
    cell_size = template_image.size[1]
    half_cell_size = cell_size // 2
    dest_size = (template_image.size[1] * width, template_image.size[1] * height)
    dest = Image.new("RGBA", dest_size)

    pos = 0
    for y in range(height):
        for x in range(width):
            tile = array[pos]

            # NORTHWEST
            im = get_template_crop(template_image, tile, TilesCorner.NORTHWEST)
            dest.paste(im, (x * cell_size, y * cell_size))

            # NORTHEAST
            im = get_template_crop(template_image, tile, TilesCorner.NORTHEAST)
            dest.paste(im, (x * cell_size + half_cell_size, y * cell_size))

            # SOUTHEAST
            im = get_template_crop(template_image, tile, TilesCorner.SOUTHEAST)
            dest.paste(im, (x * cell_size + half_cell_size, y * cell_size + half_cell_size))

            # SOUTHWEST
            im = get_template_crop(template_image, tile, TilesCorner.SOUTHWEST)
            dest.paste(im, (x * cell_size, y * cell_size + half_cell_size))

            pos += 1
    try:
        dest.save(output_filename)
    except (FileNotFoundError, OSError, SystemError) as err:
        print("Unable to save image '%s'" % output_filename)
        print("Error := %s" % err)
        return
    except:
        print("Unable to save image: '%s'" % output_filename)
        return
    return True

def parse_args():
    "Parses the arguments"
    parser = argparse.ArgumentParser(description='Autotiles Generator')
    parser.add_argument('-s', type=str, help='select a template file', metavar="template.png", default="template.png")
    parser.add_argument('-o', type=str, help='select a output file', metavar="autotile.png", default="autotile.png")
    parser.add_argument('-l', type=str, help='select a layout template', metavar="layout7x7.json", default="layout7x7.json")
    args = parser.parse_args()
    return args

def read_and_validate_layout(filename):
    """Read the JSON configuration file"""
    # Try to load the layout file.
    try:
        with open(filename) as json_file:  
            layout = json.load(json_file)
    except (FileNotFoundError, json.decoder.JSONDecodeError) as err:
        print("Unable to load the JSON layout file '%s'" % filename)
        print("Error := %s" % err)
        return None
    except:
        print("Unable to load the JSON layout file '%s'" % filename)
        return None
    return layout

def main():
    "Main entry point"
    args = parse_args()
    
    # Read the layout file.
    layout = read_and_validate_layout(args.l)
    
    # Returns if invalid.
    if layout == None:
        return

    # Generate autotiles.
    if generate_autotiles(args.s, args.o, layout["width"], layout["height"], layout["array"]):
        print("Tileset generated at '%s'!" %args.o)

    pass

if __name__ == '__main__':
    main()