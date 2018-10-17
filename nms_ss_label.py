#!/usr/bin/env python

#==============================================================================
# No Man's Sky screenshots label
#   This script copies the information from a screenshot of the visor pointed 
#   at an animal, flora or mineral and pastes a formatted version on a 
#   picture by choice.
#
#   Author: Pella86
#==============================================================================


#==============================================================================
# Imports
#==============================================================================
from gimpfu import (FG_BUCKET_FILL, CHANNEL_OP_REPLACE, NORMAL_MODE,
                    RGBA_IMAGE, EXPAND_AS_NECESSARY, PF_IMAGE, PF_DRAWABLE)

from gimpfu import pdb

from gimpfu import main, register

#==============================================================================
# Procedure functions
#==============================================================================

def adjust_perspective(drawable, new_width, new_height):
    # The text is crooked by the perspective on the HUD, this procedure levels
    # it, the proportions might be adjusted for an other resolution
    
    # upper left corner
    x0 = 0
    y0 = 0
    
    # upper right corner
    x1 = new_width
    y1 = -10
    
    # lower left corner
    x2 = 0
    y2 = 250
    
    # lower right corner
    x3 = new_width
    y3 = new_height
    
    transform_direction = 0 #TRANSFORM-FORWARD
    interpolation = 2 #INTERPOLATION-CUBIC
    supersample = 0 #ignored parameter
    recursion_level = 3
    clip_result = 1 #TRANSFORM-RESIZE-CLIP
    
    drawable = pdb.gimp_drawable_transform_perspective(drawable, x0, y0, x1, y1, x2, y2, x3, y3, transform_direction, interpolation, supersample, recursion_level, clip_result)
    
    return drawable

def select_text(image, drawable):
    # select the white stuff (text and the paw)
    sample_threshold = 55.0/255.0 # threshold is calibrated to select only text
    pdb.gimp_context_set_sample_threshold(sample_threshold)

    operation = CHANNEL_OP_REPLACE
    color = (235, 255, 255)
    
    
    pdb.gimp_image_select_color(image, operation, drawable, color)

def clear_background(image, drawable):
    # invert selection, thus selecting the background
    pdb.gimp_selection_invert(image)
    
    # clear background
    pdb.gimp_edit_clear(drawable)

    # invert selection
    pdb.gimp_selection_invert(image)    

def bucket_fill(drawable):
    fill_mode = FG_BUCKET_FILL
    paint_mode = NORMAL_MODE
    opacity = 100
    threshold = 0
    sample_merged = 0
    x = 0
    y = 0
    pdb.gimp_bucket_fill(drawable, fill_mode, paint_mode, opacity, threshold, sample_merged, x, y)    

def beautify_font(image, layer):
    
    org_width = layer.width
    org_height = layer.height

    # set FG Color to white
    foreground = (255, 255, 255)
    pdb.gimp_context_set_foreground(foreground)

    # color selection white
    bucket_fill(layer)
    
    # scale layer
    new_width = org_width * 2
    new_height = org_height * 2
    local_origin = 1 # 1 = True | 0 = False
    pdb.gimp_layer_scale(layer, new_width, new_height, local_origin)
    
    # alpha to selection
    operation = CHANNEL_OP_REPLACE
    item = layer
    pdb.gimp_image_select_item(image, operation, item)
    
    
    # bucket fill
    bucket_fill(layer)
    
    # scale back to normal
    new_width = org_width
    new_height = org_height
    local_origin = 1 # 1 = True | 0 = False
    pdb.gimp_layer_scale(layer, new_width, new_height, local_origin) 

    # alpha to selection
    operation = CHANNEL_OP_REPLACE
    item = layer
    pdb.gimp_image_select_item(image, operation, item)


def add_black_outline(image, drawable, original_layer_position, width, height, offx, offy):
    
    # make selection bigger
    steps = 3
    pdb.gimp_selection_grow(image, steps)
    
    # create new layer
    type = RGBA_IMAGE
    name = "text background"
    opacity = 100
    mode = NORMAL_MODE
    layer_textbg = pdb.gimp_layer_new(image, width, height, type, name, opacity, mode)        

    position = original_layer_position + 1
    pdb.gimp_image_add_layer(image, layer_textbg, position)

    #offset new layer by info
    pdb.gimp_layer_set_offsets(layer_textbg, offx, offy)
   
    # select layer
    image.active_layer = layer_textbg

    # set FG Color to black
    foreground = (0, 0, 0)
    pdb.gimp_context_set_foreground(foreground)   
    
    # fill selection with black
    fill_mode = FG_BUCKET_FILL
    paint_mode = NORMAL_MODE
    opacity = 100
    threshold = 0
    sample_merged = 0
    x = 0
    y = 0
    pdb.gimp_bucket_fill(layer_textbg, fill_mode, paint_mode, opacity, threshold, sample_merged, x, y)
    
    # select the text layer and merge it to the black outline
    merge_layer = image.layers[original_layer_position]
    merge_type = EXPAND_AS_NECESSARY
    layer = pdb.gimp_image_merge_down(image, merge_layer, merge_type)
    return layer


def copy_all(image, drawable):
    # select all
    pdb.gimp_selection_all(image)
    
    # copy
    non_empty = pdb.gimp_edit_copy(drawable)
    if not non_empty:
        pdb.gimp_message("Error: Copy operation failed" ) 

def paste_in_new_image(image2, ilayer, width, height, offx, offy):
    # create a new layer in the second image
    type = RGBA_IMAGE
    name = "information text {}".format(ilayer + 1)
    opacity = 100
    mode = NORMAL_MODE
    layer_info = pdb.gimp_layer_new(image2, width, height, type, name, opacity, mode)              
    
    position = 0
    pdb.gimp_image_add_layer(image2, layer_info, position) 

            
    # paste image
    drawable = image2.layers[0]
    paste_into = True
    
    floating_sel = pdb.gimp_edit_paste(drawable, paste_into)
    pdb.gimp_floating_sel_anchor(floating_sel)    
    
    # move to original visor position
    pdb.gimp_layer_set_offsets(drawable, offx, offy)



#==============================================================================
# Procedure
#==============================================================================

class CropCoords:
    
    def __init__(self, w, h, offx, offy):
        self.width = w
        self.height = h
        self.offx = offx
        self.offy = offy
    
    def crop_layer(self):
        return (self.width, self.height, -self.offx, -self.offy) 

    def add_layer(self):     
        return (self.width, self.height, self.offx, self.offy) 
    
    def get_offsets(self):
        return (self.offx, self.offy)
    
    def get_size(self):
        return (self.width, self.height)
    
def elaborate(image, drawable, image2):
    
    # insert the alpha channel 
    # after the text extraction the blue background will be deleted
    layer = image.active_layer
    pdb.gimp_layer_add_alpha(layer)
    
    # create 4 copies of the visor image
    
    ss_info_coords = [CropCoords(410, 250, 132, 334),
                      CropCoords(321, 149, 119, 606),
                      CropCoords(199, 85, 125, 239),
                      CropCoords(293, 81, 1521, 500),
                      CropCoords(228, 113, 1575, 588)]

#    ss_info_coords = [CropCoords(410, 250, 132, 334)]
    
    n_layers = len(ss_info_coords)
    
    for i in range(n_layers - 1):
        add_alpha = 1 #0 = False | 1 = True
        copy_layer = pdb.gimp_layer_copy(layer, add_alpha)
        
        position = 0
        pdb.gimp_image_add_layer(image, copy_layer, position)
    
    for ilayer in range(n_layers):
        layer = image.layers[ilayer]

        pdb.gimp_layer_resize(layer, *ss_info_coords[ilayer].crop_layer())
    
    for ilayer in range(n_layers):
        layer = image.layers[ilayer]
        select_text(image, layer)
        clear_background(image, layer)
        
        beautify_font(image, layer)
        
        
        add_black_outline(image, layer, ilayer, *ss_info_coords[ilayer].add_layer())
    
    
    for ilayer in range(n_layers):
        layer = image.layers[ilayer]
        copy_all(image, layer)
        paste_in_new_image(image2, ilayer, *ss_info_coords[ilayer].add_layer())



#==============================================================================
# Script entry  
#==============================================================================

def nms_ss_label(image, drawable, image2):
    handler = 0 #MESSAGE BOX
    pdb.gimp_message_set_handler(handler)
    
    if image and image2:
        images = [image, image2]
        right_width  = all(True if i.width == 1920 else False for i in images)
        right_height = all(True if i.height == 1080 else False for i in images)
        
        if right_width and right_height:
            elaborate(image, drawable, image2)
            pdb.gimp_message("Operation successfull")
        else:
            pdb.gimp_message("Error: Size of images must be 1920x1080")
            
    else:
        pdb.gimp_message("Error: No image loaded")

    handler = 2 # ERROR-CONSOLE
    pdb.gimp_message_set_handler(handler)    


#==============================================================================
# GIMP main and stuff registry
#==============================================================================

register(
    "python-fu-nms-ss-label",
    "This function labels No Man's Sky screenshots",
    "After providing two images, one with the visor scan view on a organism, the other with the screenshot to label, the program cuts the visor ss and pastes it on the image",
    "Pella86", "Pella86", "2018",
    "NMS Screenshot label",
    "", # type of image it works on (*, RGB, RGB*, RGBA, GRAY etc...)
    [
        (PF_IMAGE, "image", "takes current image", None),
        (PF_DRAWABLE, "drawable", "Input layer", None),
        (PF_IMAGE, "image2", "Select image where to paste the information", None)
    ],
    [],
    nms_ss_label, menu="<Image>/Games scripts")  # second item is menu location

main()