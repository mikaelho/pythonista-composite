# pythonista-composite
UI component that provides effortless stacking of other UI Views, e.g. Label on a Button.

Composite is a custom Pythonista UI View that supports stacking several other views in the same area, while providing easy access to the features of the individual views.

## Example #1 - Basic use

Let's stack a ui.Label on top of a ui.Button:

    lbl_btn = Composite(Button, Label)
    
Composite members are listed in bottom-up order, and you can provide both classes and instances; classes are simply instantiated with no arguments.

When you access or set an attribute on the composite, it is also applied in the order given to the constructor, above. Thus, if I set the alignment:

    lbl_btn.alignment = ALIGN_RIGHT
    
This applies to the Label, as Button does not have that attribute. On the other hand, setting the background color:

    lbl_btn.background_color = 'lightgrey'

Applies only to the first view, Button, even though the Label has that attribute as well.

The underlying Composite view grabs all attributes that affect the sizing and positioning of the whole composited view. For example:

    lbl_btn.center = (100, 100)

Likewise, setting the size of the Composite will lay out all the contained views so that they all fill the whole area of the Composite.   
            
If you need to explicitly manage a specific view, for example to manage which view gets touch events, you have two options:

1. Instantiate it and retain the reference to it, in order to set values before or after giving it to the Composite constructor.
2. Get the specific view by class name, and set specific values on it.

An example of the second option:

    lbl_btn['Label'].border_color = 'black'

## Example #2 - Margins and corners

Composite comes with a Margins view, which can be included to inset the following views by a set amount, by default 5 pixels from every edge:

    lbl = Composite(Margins, Label)
    
You can set the margin values for every edge separately, with any of the following options:

* single number - Same amount on all sides
* 2-tuple - (top and bottom, sides)
* 3-tuple - (top, sides, bottom)
* 4-tuple - (top, right, bottom, left)

For example:

    lbl.margin = (5, 10)
    
Sets top and bottom margins to 5 pixels, and side margins to 10 pixels.

Labels do not normally support rounded corners eithout some objc_util code, but luckily the containing View does, so this works as well:

    lbl.corner_radius = 10
    
`size_to_fit` also works as expected, arranging the whole Composite view around the preferred size of the innermost/topmost view.

## Example #3 - Shadow

Setting the shadow options for the whole Composite view is supported, either with the convenience function `set_drop_shadow` that only needs the color of the shadow as a parameter, or with the individual settings:

* shadow_opacity
* shadow_offset (tuple)
* shadow_color
* shadow_radius

## Example #4 - Blurred background

iOS BlurEffect is available through a separate auxiliary view:

    blur_lbl = Composite(Blur, Button, Label)
    
`style` option can be used to set the brightness of the blurred area in relation to the underlying layer to one of the following values:

* LIGHTER
* SAME (default)
* DARKER

## Run the examples

All of the above examples are demonstrated in the end of the `composite.py` file.

# To do

Should include the vibrancy effect as well.

Other composable examples are highly welcome, as issues or pull requests.

Thanks to the following contributions on the Pythonista forum:

* ObjC code for the [shadow settings](https://forum.omz-software.com/topic/1942/drop-shadow-behind-ui-view/15?page=2)
* [BlurView](https://forum.omz-software.com/topic/2738/ui-gaussian-blur/4) code
