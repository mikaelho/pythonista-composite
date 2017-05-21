# pythonista-composite

UI component that provides effortless stacking of other UI Views, e.g. Label on a Button.

Composite is a custom Pythonista UI View that supports stacking several other views in the same area, while providing easy access to the features of the individual views.

In addition to the stacking of views, Composite has a subclass, Chainable, that can be further used to enable easy composition of specialized components from regular ones. But first, a basic example of Composite:

## Basic Composite use

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

## Chainable

Chainable makes Composite easier to use by supporting subclassing and composing new components through multiple inheritance. Chainable is intended to be subclassed in two main ways:

* _Flavors_ have a `setup` method that sets some attributes for the view.
* _Stackers_ have `spec` method that adds one or more view to a specific position in the composite stack.

Sample flavor-type classes included are:

* `Solid` - white background
* `Semitransparent` - you guessed it
* `Rounded` - 5 pt rounded corners
* `Round` - makes a square view into a round one
* `Shadowed` - dark grey drop shadow

Sample stacker-type classes included are:

* `Clickable` - ui.Button included at the bottom of the stack
* `Blurred` - background added tot the bottom of the stack
* `Margins` - adds a margin-managing view on the top, with the expectation that something more will be added on top of it
* `Editable` - ui.TextField added on top

A subclass can of course be both a flavor and a stacker. There is one sample included:

* `DefaultLabel` - adds a Label to the stack and sets some default values such as black text and center-alignment.

New UI classes are easy to create from the flavors and stackers simply by multiclassing.

Here are the examples that you see if you run `composite.py`:

1. `SolidLabelButton` - inherits from Solid, DefaultLabel (which has Margins), Clickable
2. `FancyLabel` - inherits from Sized, Rounded, Semitransparent, DefaultLabel
3. `ContainedTextField` - inherits from Editable, Margins
4. `SizedSemitransparentLabel` - inherits from Sized, SemitransparentLabel (which in turn inherits from Semitransparent and DefaultLabel)
5. `ShadowedLabel` - inherits from Shadowed and DefaultLabel
6. `BlurRoundLabelButton` - inherits through many levels from DefaultLabel, Clickable, Round and Blurred

## Rolling your own

Samples in the previous section may be useful, but creating your own is an easy way to get the exact look and feel you need.

To create your own flavor or stacker, inherit from the Chainable and implement one or both of the following methods:

    def setup(self):
      super().setup()
      self.some_settings = some_values
      
    def spec(self):
      return [NewView] + super().spec() # Add to bottom

        or
    
      return super().spec() + [NewView] # Add to top
      
Then you can use your new class in multiple-inheritance combos, like:

    class NiceLabel(Sized, Semitransparent, DefaultLabel):
      pass
      
Note that this class does not need to implement anything, if the functionality brought in by the superclasses is sufficient.

In case you have superclasses that bring in conflicting functionality, say both define background_color, or both want to be at the bottom of the stack, the winner is defined by the execution order of the classes. The way Chainable is set up, the inherited classes will execute from right to left. For example, in the code above, DefaultLabel must be later in the list, so that it defines multiline layout before Sized does the sizing.

## Custom views

### Composite

Basic function of Composite is to maintain a stack of views, one on top of the other, so that the whole provides combined capabilities, like the Label that is also a Button.

Composite constructor expects the regular arguments to contain View instances or classes in the order they are to be stacked, from bottom to top. Keyword arguments are treated as regular ui.View keyword arguments.

Composite manages the position and the size of the whole stack, so setting the size of the Composite view resizes all the contaibed views to match. `size_to_fit` also works as expected, arranging the whole Composite view around the preferred size of the innermost/topmost view.

Internally, contained views are subviews of each other in the ascending order. Only the bottom-most view is a subview of the Composite. Composite provides access to the stacked views by their class names, i.e. a Label in the stack is accessible by composite_instance['Label'].

Composite also provides access to the shadow settings normally only accessible through objc_util. You can set the shadow options either with the convenience function `set_drop_shadow` that only needs the color of the shadow as a argument, or with the individual properties:

* shadow_opacity
* shadow_offset (tuple)
* shadow_color
* shadow_radius

### MarginView

MarginView insets the child view by a set amount, by default 5 points from every edge.
    
You can set the margin values for every edge separately, with any of the following options:

* single number - Same amount on all sides
* 2-tuple - (top and bottom, sides)
* 3-tuple - (top, sides, bottom)
* 4-tuple - (top, right, bottom, left)

For example:

    lbl.margin = (5, 10)
    
Sets top and bottom margins to 5 pixels, and side margins to 10 pixels.

### BlurView

iOS BlurEffect is available through a separate auxiliary view, BlurView.
    
`style` property can be used to set the brightness of the blurred area in relation to the underlying layer. Possible values are:

* LIGHTER
* SAME (default)
* DARKER

# To do

Should maybe include the vibrancy effect as well.

Other composable examples are highly welcome, as issues or pull requests.

Thanks to the following contributions on the Pythonista forum:

* ObjC code for the [shadow settings](https://forum.omz-software.com/topic/1942/drop-shadow-behind-ui-view/15?page=2)
* [BlurView](https://forum.omz-software.com/topic/2738/ui-gaussian-blur/4) code
