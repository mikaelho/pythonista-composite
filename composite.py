#coding: utf-8
from ui import *
from objc_util import *
from types import MethodType as as_method
from types import SimpleNamespace as sn
import numbers

class Composite(View):
  """ Simple pass-thru view that maintains a composite stack of other views. Captures position and size changes but passes all other changes to the stack of contained views. """
  
  def __init__(self, *view_classes, frame=(0, 0, 100, 100), **kwargs):
    """ Accepts view classes or instances as 
    parameters, followed by normal View keyword 
    parameters. Classes are instantiated with no 
    arguments, instances are used as is.
    
     Composite has a `flex` default setting of 
     'LRTB', but you are free to change it as
     you see fit. """

    super().__init__()
    self.pntr = ObjCInstance(self)   
    self._contained = Container(self, *view_classes)
    self.frame = frame
    self.flex = 'LRTB'
    for key in kwargs:
      setattr(self, key, kwargs[key])
    self.pntr.layer().setMasksToBounds_(False)
    
  def __getitem__(self, key):
    """ Stacked views are available by the name of the class, i.e. assumes that only one instance per class is needed in the composite. """
    
    return self._contained.name_lookup[key]
    
  def __getattr__(self, key):
    if key == '_contained' or key in Container.layout_attributes:
      return object.__getattribute__(self, key)
    return self._contained.get_attr(key)
    
  def __setattr__(self, key, value):
    if key == '_contained' or key in Container.layout_attributes:
      return object.__setattr__(self, key, value)
    return self._contained.set_attr(key, value)
  
  @property 
  def masks_to_bounds(self):
    return self.pntr.layer().masksToBounds()
        
  @masks_to_bounds.setter
  def masks_to_bounds(self, val):
    self.pntr.layer().setMasksToBounds_(val)
  
  @property
  def shadow_opacity(self):
    return self.pntr.layer().shadowOpacity()
        
  @shadow_opacity.setter
  def shadow_opacity(self, val):
    self.pntr.layer().setShadowOpacity_(val)
        
  @property
  def shadow_radius(self):
    return self.pntr.layer().shadowRadius()
        
  @shadow_radius.setter
  def shadow_radius(self, val):
    self.pntr.layer().setShadowRadius_(val)
        
  @property
  def shadow_offset(self):
    return self.pntr.layer().shadowOffset()
        
  @shadow_offset.setter
  def shadow_offset(self, offset):
    self.pntr.layer().setShadowOffset_(CGSize(*offset))
            
  @property
  def shadow_color(self):
    return self.pntr.layer().shadowColor()
        
  @shadow_color.setter
  def shadow_color(self, color):
    (red, green, blue, alpha) = parse_color(color)
    objc_color = ObjCClass('UIColor').colorWithRed_green_blue_alpha_(red, green, blue, alpha).CGColor()
    
    self.pntr.layer().setShadowColor_(objc_color)
    
  def set_drop_shadow(self, color):
    self.shadow_opacity = 1
    self.shadow_offset = (5,5)
    self.shadow_color = color
    self.shadow_radius = 5
    
  def make_round(self):
    self.corner_radius = min(self.width, self.height)/2
    
    
class Container():
  
  layout_attributes = { 'bounds', 'center', 'flex', 'frame', 'height', 'hidden', 'name', 'size_to_fit', 'transform', 'width', 'x', 'y', 'pntr', 'masks_to_bounds', 'shadow_opacity', 'shadow_radius', 'shadow_offset', 'shadow_color', 'set_drop_shadow', 'round'}
  
  def __init__(self, bottom_view, *views):
    self.bottom_view = bottom_view
    self.stack = []
    self.name_lookup = {}
    child_lookup = {}
    previous = bottom_view
    for view_spec in views:
      # Class or instance is ok
      v = view_spec if isinstance(view_spec, View) else view_spec()
      self.stack.append(v)
      previous.add_subview(v)
      # Need to manage chain explicitly as some
      # views have more than one subview
      child_lookup[previous] = v
      if not isinstance(previous, SelfLayout):
        def size_right(self):
          child = child_lookup[self]
          child.size_to_fit()
          self.width = child.width
          self.height = child.height
        def layout_right(self):
          child = child_lookup[self]
          child.frame = self.bounds
          if hasattr(child, 'layout'):
            child.layout()
        object.__setattr__(previous, 'size_to_fit', as_method(size_right, previous))
        object.__setattr__(previous, 'layout', as_method(layout_right, previous))
      v.name = type(v).__name__
      self.name_lookup[v.name] = v
      previous = v
      
  def get_attr(self, key):
    for v in self.stack:
      if hasattr(v, key):
        return getattr(v, key)
    raise AttributeError(key)
    
  def set_attr(self, key, value):
    for v in self.stack:
      if hasattr(v, key):
        return setattr(v, key, value)
    raise AttributeError(key)
    
    
class SelfLayout(View):
  """ Superclass for views that take care of their
  layouts in composites, i.e. will not use
  Composite-inserted size_to_fit and layout methods. """
    
class MarginView(SelfLayout):
  """ View that insets contained view by given
  amount from every side.
  
  Margins can be defined as:
    * single number - Same amount on all sides
    * 2-tuple - (top and bottom, sides)
    * 3-tuple - (top, sides, bottom)
    * 4-tuple - (top, right, bottom, left)
    
  (Same as CSS margins)
  """
  
  def __init__(self, margin=None, **kwargs):
    super().__init__(**kwargs)
    self._margin = sn(top=5, right=5, bottom=5, left=5)
    self.touch_enabled = False
    if margin:
      self.margin = margin
  
  @property
  def margin(self):
    return self._margin

  @property
  def top(self):
    """ Read-only """
    return self._margin.top
    
  @property
  def right(self):
    """ Read-only """
    return self._margin.right
    
  @property
  def bottom(self):
    """ Read-only """
    return self._margin.bottom
    
  @property
  def left(self):
    """ Read-only """
    return self._margin.left

  @margin.setter
  def margin(self, value):
    if isinstance(value, numbers.Number):
      value = (value, value, value, value)
    elif len(value) == 3:
      value = (value[0], value[1], value[2], value[1])
    elif len(value) == 2:
      value = (value[0], value[1], value[0], value[1])

    value = sn(top=value[0], right=value[1], bottom=value[2], left=value[3])
    if value != self._margin:
      self._margin = value
      self.set_needs_display()
  
  def size_to_fit(self):
    child = self.subviews[0]
    child.size_to_fit()
    self.frame = (
      self.left,
      self.top,
      child.width + self.left + self.right,
      child.height + self.top + self.bottom)
    
  def layout(self):
    child = self.subviews[0]
    child.frame = (
      self.left,
      self.top,
      self.width - (self.left + self.right),
      self.height - (self.top + self.bottom))
    if hasattr(child, 'layout'):
      child.layout()


class BlurView(View):
  """ Applies a blurring effect to the content layered behind the view. """
  
  LIGHTER = 0
  """ The area of the view is lighter in hue than the underlying view. """
  
  SAME = 1
  """ The area of the view is the same approximate hue of the underlying view. """
  
  DARKER = 2
  """ The area of the view is darker in hue than the underlying view. """
  
  def __init__(self, style=SAME, *args, **kwargs):
    super().__init__(self, **kwargs)
    #self.touch_enabled = False
    self._style = style
    self.effect_view = None
    self.setup_effect_view()

  @on_main_thread
  def setup_effect_view(self):
    if self.effect_view is not None:
      self.effect_view.removeFromSuperview()
    UIVisualEffectView = ObjCClass('UIVisualEffectView')
    UIBlurEffect = ObjCClass('UIBlurEffect')
    frame = (self.bounds[0], self.bounds[1]), (self.bounds[2], self.bounds[3])
    self.effect_view = UIVisualEffectView.alloc().initWithFrame_(frame).autorelease()
    effect = UIBlurEffect.effectWithStyle_(self._style)
    self.effect_view.effect = effect
    self.effect_view.setAutoresizingMask_(18)
    ObjCInstance(self).addSubview_(self.effect_view)

  @property
  def style(self):
    return self._style

  @style.setter
  def style(self, value):
    if value != self._style:
      self._style = value
      self.setup_effect_view()


class Chainable(Composite):
  def __init__(self, *args, **kwargs):
    chain_spec = self.spec()
    super().__init__(*chain_spec, **kwargs)
    self.setup()
    
  def spec(self):
    return []
    
  def setup(self):
    pass

     
# Flavors     
      
class Semitransparent(Chainable):
  def setup(self):
    super().setup()
    self.background_color = (1, 1, 1, 0.4)
    
    
class Solid(Chainable):
  def setup(self):
    super().setup()
    self.background_color = 'white'


class Sized(Chainable):
  def setup(self):
    super().setup()
    self.size_to_fit()
      
      
class Rounded(Chainable):
  def setup(self):
    super().setup()
    self.corner_radius = 5
    
      
class Round(Chainable):
  def setup(self):
    super().setup()
    self.make_round()
    
    
class Shadowed(Chainable):
  """ Black drop shadow """
  def setup(self):
    super().setup()
    self.set_drop_shadow('darkgrey')
  
  
# Stackers
          
class Blurred(Chainable):
  def spec(self):
    return [BlurView] + super().spec()
      
      
class Margins(Chainable):
  def spec(self):
    return super().spec() + [MarginView]
      
class Clickable(Chainable):
  def spec(self):
    return [Button] + super().spec()

class Editable(Chainable):
  def spec(self):
    return super().spec() + [TextField]

# Mixed

class DefaultLabel(Margins):
  """ Center-aligned, multilined default label
  with black text and 5 pt margins """
  
  def spec(self):
    return super().spec() + [Label]
    
  def setup(self):
    super().setup()
    self.number_of_lines = 0
    self.text_color = 'black'
    self.alignment = ALIGN_CENTER
      
      
# Derivatives
      
class SizedLabel(Sized, DefaultLabel):
  """ Note that the order of inheritance matters. 
  Last gets called first to set multiline 
  operation, then the sizing. In opposite order,
  sizing is done first, and multiline will 
  initially have no effect. """
    
      
class ShadowedLabel(Shadowed, DefaultLabel):
  pass
  
      
class SemitransparentLabel(Semitransparent, DefaultLabel):
  pass
    
    
class SizedSemitransparentLabel(Sized, SemitransparentLabel):
  pass

      
class LabelButton(DefaultLabel, Clickable):
  """ Turns the MarginLabel into a Button as well
  """

class SolidLabelButton(Solid, DefaultLabel, Clickable):
  pass
    
    
class SemitransparentLabelButton(Semitransparent, LabelButton):
  pass

        
class RoundLabelButton(Round, LabelButton):
  pass

    
class BlurRoundLabelButton(Blurred, RoundLabelButton):
  pass


class ContainedTextField(Editable, Margins): pass

if __name__ == '__main__':
  import console
  
  v = ImageView()
  v.image = Image.named("IMG_0419.JPG")
  v.present('sheet')
  
  # Combine label with button
  
  lbl_btn = SolidLabelButton(text = "#1 - Click me")
  lbl_btn.center = (v.width * 0.25, v.height * 0.25)
  def click_action(sender):
    console.hud_alert('Clicked', duration=0.5)
  lbl_btn.action = click_action 

  v.add_subview(lbl_btn)
  
  # Combine label with some niceties
  
  class FancyLabel(Sized, Rounded, Solid, DefaultLabel): pass
  
  lbl = FancyLabel(text = '#2 - Size-to-fit label with margins and rounded corners')
  lbl.center = (v.width * 0.75, v.height * 0.25)

  v.add_subview(lbl)

  # Text field with a rectangular border

  fld = ContainedTextField(text='#3 - Editable')
  (fld.width, fld.height) = (150, 50)
  fld.center = (v.width * 0.25, v.height * 0.5)
  # TextField does not support size_to_fit
  fld.background_color = 'lightgrey'
  
  v.add_subview(fld)
  
  # Transformed composite
  
  lbl = SizedSemitransparentLabel(text='#4 - Rotated semi-transparent composite')
  #lbl.size_to_fit()
  lbl.center = (v.width * 0.75, v.height * 0.5)

  lbl.transform = Transform.rotation(1)
  
  v.add_subview(lbl)
  
  # Drop shadow built in
  
  shadow_lbl = ShadowedLabel(text='#5 - Label with drop shadow')
  shadow_lbl.size_to_fit()
  shadow_lbl.center = (v.width * 0.25, v.height * 0.75)
  
  shadow_lbl.background_color = '#F29C50'
  shadow_lbl.shadow_color = '#D46247'

  v.add_subview(shadow_lbl)
  
  # Go for the blur
  
  blur_lbl = BlurRoundLabelButton(text= '#6 - Blur button', action=click_action)
  blur_lbl.center = (v.width * 0.75, v.height * 0.75)

  v.add_subview(blur_lbl)


