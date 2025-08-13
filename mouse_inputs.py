# from inputs import get_gamepad
import pyautogui
import pydirectinput
# import time
import math
import sounddevice as sd
import soundfile as sf
import threading
import time



# from collections import deque

import math
import pyautogui
from collections import deque

class SmoothMouseController:

    def __init__(self):
        # getting screen size
        self.max_screen_width, self.max_screen_height = pyautogui.size()

        # mouse angles and values
        self.last_updated_value = 0  # Store the last raw input that caused an update
        self.last_output = 0.0       # Store the last output radians value
        self.current_angle = math.pi/2
        self.default_angle = math.pi/2
        
        # For linear interpolation smoothing
        self.current_x = None
        self.current_y = None
        
        # For threshold-based updates (performance optimization)
        self.last_target_x = None
        self.last_target_y = None

    
    def abs_x_to_relative_radians(self, abs_x_value,
                                  dead_zone=100,
                                  max_angle_degrees=270,
                                  threshold=200):
        """
        Convert ABS_X input directly to relative radians using normalized input
        Only updates when input moves more than dead_zone amount from last updated value
        
        Args:
            abs_x_value: Input value (-32768 to 32767)
            dead_zone: Range around 0 that counts as "no movement" AND
                      minimum change required from last updated value
            max_angle_degrees: Maximum angle in each direction
        
        Returns:
            radians: Relative angle from starting position
                    0 = no movement
                    positive = clockwise 
                    negative = counterclockwise
        """

        abs_x_value = -abs_x_value 

        # Check if we've moved enough from the last updated value to warrant an update
        if abs(abs_x_value - self.last_updated_value) < threshold:
            return self.last_output
        
        # Dead zone check (center dead zone)
        if abs(abs_x_value) <= dead_zone:
            # Update our tracking values
            self.last_updated_value = abs_x_value
            self.last_output = 0.0
            return 0.0
        
        # Convert max angle to radians
        max_angle_radians = math.radians(max_angle_degrees)
        
        # Normalize the input to -1.0 to 1.0 range (outside dead zone)
        if abs_x_value > dead_zone:
            # Positive side: map (dead_zone, 32767] to (0, 1]
            normalized = (abs_x_value - dead_zone) / (32767 - dead_zone)
        elif abs_x_value < -dead_zone:
            # Negative side: map [-32768, -dead_zone) to [-1, 0)
            normalized = (abs_x_value + dead_zone) / (32768 - dead_zone)
        else:
            # This shouldn't happen due to dead zone check above
            normalized = 0.0
        
        # Clamp to [-1, 1] range
        normalized = max(-1.0, min(1.0, normalized))
        
        # Convert to radians
        new_output = normalized * max_angle_radians
        
        # Update our tracking values since we're returning a new value
        self.last_updated_value = abs_x_value
        self.last_output = new_output
        
        return new_output


    def radians_to_mouse_position(self, relative_radians, center_x, 
                                  center_y, radius, 
                                  starting_angle_radians=None,
                                  lerp_factor=0.15,
                                  pixel_threshold=3):
        """
        Convert radians to actual mouse coordinates with combined threshold + lerp smoothing
        
        Args:
            relative_radians: Offset from abs_x_to_relative_radians()
            starting_angle_radians: Where mouse starts on circle
            center_x, center_y: Center of the circle
            radius: Circle radius in pixels
            lerp_factor: How much to move toward target each frame (0.05-0.3)
                        Lower = smoother but more lag
                        Higher = more responsive but less smooth
            pixel_threshold: Only update target if movement exceeds this many pixels
                           Reduces unnecessary calculations and micro-movements
        
        Returns:
            (x, y): Smoothed mouse coordinates
        """
        if starting_angle_radians is None:
            final_angle = self.default_angle + relative_radians
        else:
            final_angle = self.current_angle
        
        # Calculate new target coordinates
        new_target_x = center_x + radius * math.cos(final_angle)
        new_target_y = center_y - radius * math.sin(final_angle)
        
        # Initialize if first call
        if self.current_x is None:
            self.current_x = new_target_x
            self.current_y = new_target_y
            self.last_target_x = new_target_x
            self.last_target_y = new_target_y
        
        # Check if new target has moved enough to warrant an update (threshold check)
        if self.last_target_x is not None and self.last_target_y is not None:
            distance_moved = math.sqrt((new_target_x - self.last_target_x)**2 + 
                                     (new_target_y - self.last_target_y)**2)
            
            # Only update target if we've moved beyond threshold
            if distance_moved >= pixel_threshold:
                self.last_target_x = new_target_x
                self.last_target_y = new_target_y
            else:
                # Use previous target to avoid micro-movements
                new_target_x = self.last_target_x
                new_target_y = self.last_target_y
        else:
            # First run, set the target
            self.last_target_x = new_target_x
            self.last_target_y = new_target_y
        
        # Linear interpolation toward target (always lerp for smoothness)
        self.current_x += (new_target_x - self.current_x) * lerp_factor
        self.current_y += (new_target_y - self.current_y) * lerp_factor
        
        # Ensure coordinates are within screen bounds
        final_x = max(0, min(self.max_screen_width - 1, int(self.current_x)))
        final_y = max(0, min(self.max_screen_height - 1, int(self.current_y)))

        # saving the current angle for future reference
        self.current_angle = final_angle

        return final_x, final_y
       
class GameScreenMouse(SmoothMouseController):
    def __init__(self):
        super().__init__()
        # mouse starting position distance from center
        self.character_radius = 40  # character radius in pixels
        self.attack_rang = 200  # attack range in pixels
        self.walk_range = 500  # walk range in pixels

        self.original_radius = self.attack_rang
        self.current_radius = self.original_radius 
        
        self.lock_mouse = True

        self.curr_radian_val = 0.0

        # offsets per side
        self.offset_x = -90
        self.offset_y = -45
        self.curr_side = 'blue'
        self.offset_blue = [-90, -45]
        self.offset_red = [70, -170]

        # champion center position
        self.center_x = (self.max_screen_width // 2) + self.offset_x
        self.center_y = (self.max_screen_height // 2) + self.offset_y

    def _center_mouse(self):
        ''' ONLY FOR TESTING PURPOSES '''
        self.move_mouse(self.center_x, self.center_y)


    def quarter_step_mouse(self, cardinal_direction='N'):
        """Move the mouse in a quarter step based on cardinal direction."""
        if cardinal_direction == 'N':
            self.default_angle = math.pi / 2
        elif cardinal_direction == 'E':
            self.default_angle = 0
        elif cardinal_direction == 'S':
            self.default_angle = -math.pi / 2
        elif cardinal_direction == 'W':
            self.default_angle = math.pi

        # Rotate the mouse to the new angle
        self.rotate_mouse(self.current_radius)

    def rotate_mouse(self, abs_x_value, starting_angle_radians=None):       

        radian_val = self.abs_x_to_relative_radians(int(abs_x_value))
        
        X_POS, Y_POS = self.radians_to_mouse_position(radian_val,
                                                    self.center_x,
                                                    self.center_y,
                                                    self.current_radius,
                                                    starting_angle_radians)

        if X_POS >= self.max_screen_width:
            X_POS = self.max_screen_width - 100
        elif X_POS <= 0:
            X_POS = 10

        if Y_POS >= self.max_screen_height:
            Y_POS = self.max_screen_height - 100
        elif Y_POS <= 0:
            Y_POS = 10

        self.move_mouse(X_POS, Y_POS)

    # def absolute_mouse_move(self):
    #     # start by moving mouse to correct position
    #     items_cord_x = 1070
    #     items_cord_y = 960
        
    #     self.move_mouse(items_cord_x, items_cord_y)

    def modify_radius(self, input_val):

        # changing the radius
        modify_val = input_val

        if modify_val < 0:
            self.current_radius = self.original_radius + modify_val/2
        else:
            self.current_radius = self.original_radius + modify_val


        if self.current_radius < self.character_radius:
            self.current_radius = self.character_radius

        self.rotate_mouse(self.current_radius,
                    starting_angle_radians=self.current_angle)


    def set_radius(self, radius_size):
        '''
        radius_size: string  
            'small' - charcater radius
            'medium' - combat radius
            'large' - clicking radius
            'verylarge' - drifting radius
        '''
        if radius_size == 'small':
            self.current_radius = self.character_radius

        elif radius_size == 'medium':
            self.current_radius = self.attack_rang
        
        elif radius_size == 'large':
            self.current_radius = self.walk_range

        
        self.rotate_mouse(self.current_radius, 
                          starting_angle_radians=self.current_angle)
      
    def shop_offset(self):
        if [self.offset_x, self.offset_y] == [0, 0]:
            if self.curr_side == 'blue':
                self.offset_x, self.offset_y = self.offset_blue
            elif self.curr_side == 'red':
                self.offset_x, self.offset_y = self.offset_red

        else:
            self.offset_x, self.offset_y = 0, 0
        
        self.center_x = (self.max_screen_width // 2) + self.offset_x
        self.center_y = (self.max_screen_height // 2) + self.offset_y
            
        
    def swap_offset_side(self):
        if self.curr_side == 'blue':
            self.offset_x, self.offset_y = self.offset_red
            self.curr_side = 'red'
        else:
            self.offset_x, self.offset_y = self.offset_blue
            self.curr_side = 'blue'

        self.center_x = (self.max_screen_width // 2) + self.offset_x
        self.center_y = (self.max_screen_height // 2) + self.offset_y
        

    def move_mouse(self, x, y):
        def move_mouse_thread():
            """Move the mouse to the specified coordinates."""
            pyautogui.moveTo(x, y)
        
        """Simulate mouse movement."""
        threading.Thread(target=move_mouse_thread).start()
    
    def click_mouse(self, button='right', shift=False):
        def click_func():
            """Click the mouse button."""
            if button == 'right':
                pydirectinput.mouseDown(button='right')
                pydirectinput.mouseUp(button='right')
            elif button == 'left':
                pydirectinput.mouseDown(button='left')
                pydirectinput.mouseUp(button='left')

        def shift_click_func():
            pydirectinput.keyDown('shift')
            pydirectinput.mouseDown(button='right')
            pydirectinput.keyUp('shift')
            pydirectinput.mouseUp(button='right')
  
        if shift:
            threading.Thread(target=shift_click_func).start()
        else:
            threading.Thread(target=click_func).start()

   
if __name__ == "__main__":

    from controller_read import Controller

    controller = Controller()
    mouse = GameScreenMouse()

    while True:
        # Read controller input
        controller.read()

        # Rotate mouse based on ABS_X input
        mouse.rotate_mouse(controller.buttons['ABS_X'])

        # Update radius based on ABS_Y input
        controller.update_pedals()
