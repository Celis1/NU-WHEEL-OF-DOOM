# from inputs import get_gamepad
import pyautogui
import pydirectinput
# import time
import math
import sounddevice as sd
import soundfile as sf
import threading

       
class GameScreenMouse:
    def __init__(self):
        # getting screen size
        self.max_screen_width, self.max_screen_height = pyautogui.size()

        # radius for mouse movement
        self.default_radius = 90
        self.current_radius = self.default_radius
        self.max_radius = 450
        self.radius_modifier = .003

        self.current_angle = math.pi/2
        self.default_angle = math.pi/2

        self.curr_radian_val = 0.0

        # offsets per side
        self.offset_x = -90
        self.offset_y = -60
        self.curr_side = 'blue'
        self.offset_blue = [-90, -60]
        self.offset_red = [90, -00]

        # champion center position
        self.center_x = (self.max_screen_width // 2) + self.offset_x
        self.center_y = (self.max_screen_height // 2) + self.offset_y

    def _center_mouse(self):
        ''' ONLY FOR TESTING PURPOSES '''
        self.move_mouse(self.center_x, self.center_y)

    def radians_to_mouse_position(self, relative_radians, center_x, 
                                  center_y, radius, 
                                  starting_angle_radians=None):
        """
        Convert radians to actual mouse coordinates (FIXED VERSION)
        
        Args:
            relative_radians: Offset from abs_x_to_relative_radians()
            starting_angle_radians: Where mouse starts on circle
            center_x, center_y: Center of the circle
            radius: Circle radius in pixels
        
        Returns:
            (x, y): Mouse coordinates
        """
        if starting_angle_radians is None:
            final_angle = self.default_angle + relative_radians
        else:
            final_angle = self.current_angle
        
        x = center_x + radius * math.cos(final_angle)
        # FIX: Flip the Y coordinate to match screen coordinate system
        y = center_y - radius * math.sin(final_angle)
        
        # Ensure coordinates are within screen bounds
        x = max(0, min(self.max_screen_width - 1, int(x)))
        y = max(0, min(self.max_screen_height - 1, int(y)))

        # saving the current angle for future reference
        self.current_angle = final_angle

        return x, y
    
    def rotate_mouse(self, abs_x_value, starting_angle_radians=None):
        radian_val = self.abs_x_to_relative_radians(int(abs_x_value))
        
        X_POS, Y_POS = self.radians_to_mouse_position(radian_val,
                                                      self.center_x,
                                                      self.center_y,
                                                      self.current_radius,
                                                      starting_angle_radians)
                                                      
        self.move_mouse(X_POS, Y_POS)
        # print(f"Mouse moved to: ({X_POS}, {Y_POS}) with radians: {radian_val}")

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

    # TODO: GET ITEM SWAPPING FOR RANKED PLAY
    def absolute_mouse_move(self):
        # start by moving mouse to correct position
        items_cord_x = 1070
        items_cord_y = 960
        
        self.move_mouse(items_cord_x, items_cord_y)


    # TODO: MAKE BUCKETS FOR MOUSE INCRAMENTS
    def grow_radius(self, input_val):
        """Increase the radius for mouse movement."""
        incrament = abs(input_val) * self.radius_modifier

        self.current_radius = self.current_radius + incrament

        self.current_radius += incrament
        if self.current_radius > self.max_radius:
            self.current_radius = self.max_radius

        # we now want the mouse to move to the top of the new radius as it grows

        self.rotate_mouse(self.current_radius,
                            starting_angle_radians=self.current_angle)
         
    def shrink_radius(self, input_val):
        """Decrease the radius for mouse movement."""
        decrament = abs(input_val) * self.radius_modifier

        self.current_radius = abs(self.current_radius) - decrament

        if self.current_radius < self.default_radius:
            self.current_radius = self.default_radius

        self.rotate_mouse(self.current_radius,
                    starting_angle_radians=self.current_angle)

    def set_radius_max(self):
        """Set the radius to the maximum value."""
        self.current_radius = self.max_radius
        self.rotate_mouse(self.current_radius, 
                          starting_angle_radians=self.current_angle)
        
    def set_radius_min(self):
        """Reset the radius to the default value."""
        self.current_radius = self.default_radius
        self.rotate_mouse(self.current_radius, 
                          starting_angle_radians=self.current_angle)
        
    def set_radius_attack_range(self):
        """Set the radius to the attack range."""
        self.current_radius = self.default_radius + 70
        self.rotate_mouse(self.current_radius, 
                          starting_angle_radians=self.current_angle)
        
    def shop_offset(self):
        print('-----SWAAPPING TO BUY SHOP SIDE-----')

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
    
    def click_mouse(self, button='right'):
        def click_mouse_thread():
            """Click the mouse button."""
            if button == 'right':
                pydirectinput.mouseDown(button='right')
                pydirectinput.mouseUp(button='right')
            elif button == 'left':
                pydirectinput.mouseDown(button='left')
                pydirectinput.mouseUp(button='left')

        threading.Thread(target=click_mouse_thread).start()

    def abs_x_to_relative_radians(self, abs_x_value,
                                  dead_zone=400,
                                  max_angle_degrees=180):
        """
        Convert ABS_X input directly to relative radians using normalized input
        
        Args:
            abs_x_value: Input value (-32768 to 32767)
            dead_zone: Range around 0 that counts as "no movement"
            max_angle_degrees: Maximum angle in each direction
        
        Returns:
            radians: Relative angle from starting position
                    0 = no movement
                    positive = clockwise 
                    negative = counterclockwise
        """

        abs_x_value = -abs_x_value 

        # Dead zone check
        if abs(abs_x_value) <= dead_zone:
            return 0.0
        
        # Convert max angle to radians
        max_angle_radians = math.radians(max_angle_degrees)
        
        # Normalize the input to -1.0 to 1.0 range (outside dead zone)
        if abs_x_value > 0:
            # Positive side: map (dead_zone, 32767] to (0, 1]
            normalized = (abs_x_value - dead_zone) / (32767 - dead_zone)
        else:
            # Negative side: map [-32768, -dead_zone) to [-1, 0)
            normalized = (abs_x_value + dead_zone) / (32767 - dead_zone)
        
        # Clamp to [-1, 1] range
        normalized = max(-1.0, min(1.0, normalized))
        
        # Convert to radians
        return normalized * max_angle_radians
