#!/usr/bin/env python

# Tutorial available at: https://www.youtube.com/watch?v=nmb-0KcgXzI

from gimpfu import *

def civ_minimap(image, drawable):
    # insert the alpha channel
    layer = image.active_layer
    pdb.gimp_layer_add_alpha(layer)

    # crop the image
    new_width = 257
    new_height = 140
    offx = 14
    offy = 918
    
    pdb.gimp_image_crop(image, new_width, new_height, offx, offy)    
    
#    propagate_mode = 0 # white
#    propagating_channel = 0
#    propagating_rate = 0 # 0 to 1
#    direction_mask = 0 # 0 to 15
#    lower_limit = 0 # 0 to 255
#    upper_limit = 0 # 0 to 255
#    pdb.plug_in_erode(image, drawable, propagate_mode, propagating_channel, propagating_rate, direction_mask, lower_limit, upper_limit)
    
    # blur the image
    horizontal = 3
    vertical = 3
    method = 1 # RLE method
    pdb.plug_in_gauss(image, drawable, horizontal, vertical, method)
    
    # select the shitty view rectangle
    color = (170, 154, 170)
    threshold = 40/255.0
    operation =  CHANNEL_OP_REPLACE
    
    pdb.gimp_context_set_sample_threshold(threshold)
    
    pdb.gimp_image_select_color(image, operation, drawable, color)


register(
    "python-fu-Civilizations-minimap",
    "The script should automatically beautyfy the minimap",
    "First attempt at making sense of the minimap",
    "Jackson Bates", "Jackson Bates", "2015",
    "Civ minimap beautyfier",
    "", # type of image it works on (*, RGB, RGB*, RGBA, GRAY etc...)
    [
        # basic parameters are: (UI_ELEMENT, "variable", "label", Default)
        (PF_IMAGE, "image", "takes current image", None),
        (PF_DRAWABLE, "drawable", "Input layer", None)
        # PF_SLIDER, SPINNER have an extra tuple (min, max, step)
        # PF_RADIO has an extra tuples within a tuple:
        # eg. (("radio_label", "radio_value), ...) for as many radio buttons
        # PF_OPTION has an extra tuple containing options in drop-down list
        # eg. ("opt1", "opt2", ...) for as many options
        # see ui_examples_1.py and ui_examples_2.py for live examples
    ],
    [],
    civ_minimap, menu="<Image>/Game scripts")  # second item is menu location

main()