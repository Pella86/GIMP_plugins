#!/usr/bin/env python

# Tutorial available at: https://www.youtube.com/watch?v=nmb-0KcgXzI

from gimpfu import *

def hello_warning(image, drawable, image2):
    if image:
        pdb.gimp_message("current image: " + image.name )
        
        # insert the alpha channel
        layer = image.active_layer
        pdb.gimp_layer_add_alpha(layer)
        
        
        # crop the image
        new_width = 410
        new_height = 250
        offx = 118 + 14
        offy = 322 + 12
        
        pdb.gimp_image_crop(image, new_width, new_height, offx, offy)
        
        # adjust the perspective
        drawable = image.active_layer
        
        # upper left
        x0 = 0
        y0 = 0
        
        # upper right
        x1 = new_width
        y1 = -10
        
        # lower left
        x2 = 0
        y2 = 250
        
        # lower right
        x3 = new_width
        y3 = new_height
        
        transform_direction = 0 #TRANSFORM-FORWARD
        interpolation = 2 #INTERPOLATION-CUBIC
        supersample = 0 #ignored parameter
        recursion_level = 3
        clip_result = 1 #TRANSFORM-RESIZE-CLIP
        drawable = pdb.gimp_drawable_transform_perspective(drawable, x0, y0, x1, y1, x2, y2, x3, y3, transform_direction, interpolation, supersample, recursion_level, clip_result)
        
        # select the white stuff
        operation = CHANNEL_OP_REPLACE
        color = (235, 255, 255)
        sample_threshold = 60.0/255.0
        
        pdb.gimp_context_set_sample_threshold(sample_threshold)
        
        pdb.gimp_image_select_color(image, operation, drawable, color)
        
        # set FG Color to white
        foreground = (255, 255, 255)
        pdb.gimp_context_set_foreground(foreground)
        
        # color selection white
        fill_mode = FG_BUCKET_FILL
        paint_mode = NORMAL_MODE
        opacity = 100
        threshold = 0
        sample_merged = 0
        x = 0
        y = 0
        pdb.gimp_bucket_fill(drawable, fill_mode, paint_mode, opacity, threshold, sample_merged, x, y)
        
        # invert selection
        pdb.gimp_selection_invert(image)
        
        # delete stuff
        pdb.gimp_edit_clear(drawable)

        # invert selection again
        pdb.gimp_selection_invert(image)
        
        # make selection bigger
        steps = 3
        pdb.gimp_selection_grow(image, steps)
        
        # create new layer
        width = image.active_layer.width
        height = image.active_layer.height
        type = RGBA_IMAGE
        name = "text background"
        opacity = 100
        mode = NORMAL_MODE
        layer_textbg = pdb.gimp_layer_new(image, width, height, type, name, opacity, mode)        
        
        position = 1
        pdb.gimp_image_add_layer(image, layer_textbg, position)
        
#        # select layer
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
        
        # select layer '0
        merge_layer = image.layers[0]
        merge_type = EXPAND_AS_NECESSARY
        layer = pdb.gimp_image_merge_down(image, merge_layer, merge_type)  
        
        # select all
        pdb.gimp_selection_all(image)
        
        # copy
        drawable = image.active_layer
        non_empty = pdb.gimp_edit_copy(drawable)
        if non_empty:
            pdb.gimp_message("copy successful" )
            
        # create a new layer in the second image
        width = new_width
        height = new_height
        type = RGBA_IMAGE
        name = "information text"
        opacity = 100
        mode = NORMAL_MODE
        layer_info = pdb.gimp_layer_new(image2, width, height, type, name, opacity, mode)              
        
        position = 0
        pdb.gimp_image_add_layer(image2, layer_info, position) 

                
        # paste image
        
        drawable = image2.active_layer
        paste_into = True
        
        floating_sel = pdb.gimp_edit_paste(drawable, paste_into)
        pdb.gimp_floating_sel_anchor(floating_sel)
        
    else:
        pdb.gimp_message("No image loaded")
    

register(
    "python-fu-Hello-Warning",
    "simply a test",
    "simply a test but longer description",
    "Me", "Myself", "2018",
    "Hello warning",
    "", # type of image it works on (*, RGB, RGB*, RGBA, GRAY etc...)
    [
        # basic parameters are: (UI_ELEMENT, "variable", "label", Default)
        (PF_IMAGE, "image", "takes current image", None),
        (PF_DRAWABLE, "drawable", "Input layer", None),
        (PF_IMAGE, "image2", "Select image where to paste the information", None)
        # PF_SLIDER, SPINNER have an extra tuple (min, max, step)
        # PF_RADIO has an extra tuples within a tuple:
        # eg. (("radio_label", "radio_value), ...) for as many radio buttons
        # PF_OPTION has an extra tuple containing options in drop-down list
        # eg. ("opt1", "opt2", ...) for as many options
        # see ui_examples_1.py and ui_examples_2.py for live examples
    ],
    [],
    hello_warning, menu="<Image>/My scripts")  # second item is menu location

main()