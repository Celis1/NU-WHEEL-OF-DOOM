from inputs import get_gamepad
import pyautogui
import pydirectinput
import time
import math
import sounddevice as sd
import soundfile as sf



class GameScreenMouse:
    def __init__(self):
        # getting screen size
        self.max_screen_width, self.max_screen_height = pyautogui.size()
        self.center_x = self.max_screen_width // 2
        self.center_y = self.max_screen_height // 2
        
        # radius for mouse movement
        self.default_radius = 50
        self.current_radius = self.default_radius
        self.max_radius = 450

        # offsets and dead zone
        self.offset_x = 0
        self.offset_y = 0
        self.dead_zone = 8192

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
        pyautogui.moveTo(X_POS, Y_POS)
        # print(f"Mouse moved to: ({X_POS}, {Y_POS}) with radians: {radian_val}")

    def center_mouse(self):
        """Center the mouse cursor on the screen."""
        screen_width, screen_height = pyautogui.size()
        center_x, center_y = screen_width // 2, screen_height // 2
        pyautogui.moveTo(center_x, center_y)


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





class Controller(GameScreenMouse):
    def __init__(self):
        super().__init__()
        self.current_event = {'ABS_X': 0,
                              'ABS_HAT0Y': 0,
                              'ABS_RY': 0,
                              'ABS_Z': 0,
                              'ABS_HAT0X': 0,
                              'ABS_RZ': 0,
                              'BTN_TR': 0,
                              'BTN_SOUTH': 0,
                              'BTN_START': 0,
                              'BTN_SELECT': 0,
                              'BTN_NORTH': 0,
                              'BTN_WEST': 0,
                              'BTN_TL': 0,
                              'BTN_EAST': 0,
                              'BTN_THUMBR': 0,
                              'BTN_THUMBL': 0,
                            }
        
        # Add previous state for debouncing
        self.previous_event = self.current_event.copy()
        
        # Track last mouse position to avoid unnecessary moves
        self.last_abs_x = 0
        self.mouse_threshold = 1000  # Only move mouse if change is significant

    def read(self):
        events = get_gamepad()
        for event in events:
            self.current_event[event.code] = event.state
            # Remove print statement for performance
            # print(event)  # COMMENT OUT THIS LINE

        return self.current_event

    def button_just_pressed(self, button):
        """Check if button was just pressed (not held)"""
        return (self.current_event[button] == 1 and 
                self.previous_event[button] == 0)

    def get_action(self):
        # Only process button presses when they're first pressed, not held
        
        # [FRONT L: BTN_TL] + other buttons
        if self.current_event['BTN_TL'] == 1:
            if self.button_just_pressed('BTN_NORTH'):
                pydirectinput.press('d')
            elif self.button_just_pressed('BTN_EAST'):
                pydirectinput.press('f')
            elif self.button_just_pressed('BTN_SOUTH'):
                pydirectinput.press('s')
            elif self.button_just_pressed('BTN_WEST'):
                pydirectinput.press('4')

        # [FRONT R: BTN_TR] + D-PAD
        elif self.current_event['BTN_TR'] == 1:
            if self.current_event['ABS_HAT0X'] == -1 and self.previous_event['ABS_HAT0X'] != -1:
                pydirectinput.press('1')
            elif self.current_event['ABS_HAT0Y'] == -1 and self.previous_event['ABS_HAT0Y'] != -1:
                pydirectinput.press('2')
            elif self.current_event['ABS_HAT0X'] == 1 and self.previous_event['ABS_HAT0X'] != 1:
                pydirectinput.press('3')

        # [BACK R: BTN_THUMBR] + D-PAD
        elif self.current_event['BTN_THUMBR'] == 1:
            if self.current_event['ABS_HAT0Y'] == -1 and self.previous_event['ABS_HAT0Y'] != -1:
                self.center_mouse()

        # Individual buttons - only when first pressed
        elif self.button_just_pressed('BTN_NORTH'):
            pydirectinput.press('w')
        elif self.button_just_pressed('BTN_SOUTH'):
            pydirectinput.press('q')
        elif self.button_just_pressed('BTN_EAST'):
            pydirectinput.press('e')
        elif self.button_just_pressed('BTN_WEST'):
            pydirectinput.press('r')

        # Right click - only when first pressed
        elif self.button_just_pressed('BTN_TR'):
            pydirectinput.mouseDown(button='right')
            pydirectinput.mouseUp(button='right')

        # Special buttons
        elif self.button_just_pressed('BTN_SELECT'):
            self.play_horn_sound()
            pydirectinput.press('u')
        elif self.button_just_pressed('BTN_START'):
            print("All chat flame macro triggered")
            self.flame_macro()

        # Triggers (these can be continuous)
        if self.current_event['ABS_RZ'] != 0:
            inc_val = max(1, self.current_event['ABS_RZ'] // 1000)  # Reduce sensitivity
            self.grow_radius(inc_val)
        if self.current_event['ABS_Z'] != 0:
            dec_value = max(1, self.current_event['ABS_Z'] // 1000)  # Reduce sensitivity
            self.shrink_radius(dec_value)

        # Update previous state
        self.previous_event = self.current_event.copy()

    def should_move_mouse(self, abs_x_value):
        """Only move mouse if there's significant change"""
        change = abs(abs_x_value - self.last_abs_x)
        if change > self.mouse_threshold or abs(abs_x_value) > self.dead_zone:
            self.last_abs_x = abs_x_value
            return True
        return False


# Optimized main loop
if __name__ == "__main__":
    controller = Controller()
    print("Starting Wheel of Doom controller...")
    
    while True:
        values = controller.read()
        
        # Only move mouse when necessary
        if controller.should_move_mouse(values['ABS_X']):
            controller.rotate_mouse(values['ABS_X'])
        
        controller.get_action()
        
        # Remove print statements for performance
        # print(values)  # COMMENT OUT THIS LINE
        
        # Small sleep to prevent CPU overload
        time.sleep(0.001)  # 1ms delay