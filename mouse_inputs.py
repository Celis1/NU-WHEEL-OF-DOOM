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
        self.default_radius = 110
        self.current_radius = self.default_radius
        self.max_radius = 450

        # offsets and dead zone
        self.offset_x = -80
        self.offset_y = -80
        self.dead_zone = 8192

        # champion center position
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
                                  dead_zone=8192,
                                  max_angle_degrees=180):
        """
        Convert ABS_X input directly to relative radians using normalized input
        
        Args:
            abs_x_value: Input value (-32768 to 32767)
            dead_zone: Range around 0 that counts as "no movement"
            max_angle_degrees: Maximum angle in each direction (default 180°)
        
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

    def radians_to_mouse_position(self, relative_radians, center_x, 
                                  center_y, radius, 
                                  starting_angle_radians=math.pi/2):
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
        final_angle = starting_angle_radians + relative_radians
        
        x = center_x + radius * math.cos(final_angle)
        # FIX: Flip the Y coordinate to match screen coordinate system
        y = center_y - radius * math.sin(final_angle)  # Notice the MINUS sign!
        
        # Ensure coordinates are within screen bounds
        x = max(0, min(self.max_screen_width - 1, int(x)))
        y = max(0, min(self.max_screen_height - 1, int(y)))

        return x, y
    
    def rotate_mouse(self, abs_x_value):
        radian_val = self.abs_x_to_relative_radians(int(abs_x_value))
        X_POS, Y_POS = self.radians_to_mouse_position(radian_val,
                                                      self.center_x,
                                                      self.center_y,
                                                      self.current_radius)
        self.move_mouse(X_POS, Y_POS)
        # print(f"Mouse moved to: ({X_POS}, {Y_POS}) with radians: {radian_val}")

    def center_mouse(self):
        """Center the mouse cursor on the screen."""
        self.move_mouse(self.center_x, self.center_y)


    def grow_radius(self, increment=10):
        """Increase the radius for mouse movement."""
        print(f"Current radius before increment: {self.current_radius}")
        self.current_radius += increment
        if self.current_radius > self.max_radius:
            self.current_radius = self.max_radius

        # we now want the mouse to move to the top of the new radius as it grows
        self.rotate_mouse(self.current_radius)

    def shrink_radius(self, decrement=10):
        """Decrease the radius for mouse movement."""
        print(f"Current radius before decrement: {self.current_radius}")
        self.current_radius -= decrement
        if self.current_radius < self.default_radius:
            self.current_radius = self.default_radius

        self.rotate_mouse(self.current_radius)

