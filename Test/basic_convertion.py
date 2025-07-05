
from inputs import get_gamepad
import pyautogui
import pydirectinput
import time
import math

#CONSTANTS
RADIUS = 300
MAX_SCREEN_WIDTH, MAX_SCREEN_HEIGHT = pyautogui.size()
CENTER_X = MAX_SCREEN_WIDTH // 2
CENTER_Y = MAX_SCREEN_HEIGHT // 2
def abs_x_to_relative_radians(abs_x_value, dead_zone=8192, max_angle_degrees=180):
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
    abs_x_value = -abs_x_value  # <- ADD THIS LINE


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

def radians_to_mouse_position(relative_radians, starting_angle_radians=math.pi/2, center_x=CENTER_X, center_y=CENTER_Y, radius=RADIUS):
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
    x = max(0, min(MAX_SCREEN_WIDTH - 1, int(x)))
    y = max(0, min(MAX_SCREEN_HEIGHT - 1, int(y)))
    
    return x, y

def center_mouse():
    """Center the mouse cursor on the screen."""
    screen_width, screen_height = pyautogui.size()
    center_x, center_y = screen_width // 2, screen_height // 2
    pyautogui.moveTo(center_x, center_y)

def main():
    """Just print out some event infomation when the gamepad is used."""
    while 1:
        events = get_gamepad()
        for event in events:
            print(event.ev_type, event.code, event.state)

            # ----- PADDLE SHIFTERS -----
            if event.code == 'BTN_TL':
                if event.state == 1:
                    print("Left paddle shifter pressed")
                    center_mouse()

            if event.code == 'BTN_TR':
                if event.state == 1:
                    print("Right paddle shifter pressed")
                    # pydirect input right click
                    pydirectinput.click(button='right')

                elif event.state == 0:
                    print("Right paddle shifter released")
                    # pydirect input right click release
                    pydirectinput.mouseUp(button='right')

            # ----- D-PAD -----

            # ----- BUTTON PRESSES -----
            if event.code == 'BTN_NORTH':
                if event.state == 1:
                    print("Button North pressed")
                    # pyautogui.typewrite('Hello, World!', interval=0.1)
                    pydirectinput.press('w')

            if event.code == 'BTN_EAST':
                if event.state == 1:
                    print("Button East pressed")
                    pydirectinput.press('d')

            if event.code == 'BTN_SOUTH':
                if event.state == 1:
                    print("Button South pressed")
                    pydirectinput.press('a')

            if event.code == 'BTN_WEST':
                if event.state == 1:
                    print("Button West pressed")
                    pydirectinput.click(button='middle')

            # ----- TRIGGERS -----
            if event.code == 'ABS_RZ':
                if event.state == 1:
                    print("Right  trigger pressed")

            if event.code == 'ABS_Z':
                if event.state == 1:
                    print("Left trigger pressed")


            # ----- WINDOWS BUTTONS -----
            if event.code == 'BTN_SELECT':
                if event.state == 1:
                    print("HORN HAS BEEN PRESSED")

            if event.code == 'BTN_START':
                if event.state == 1:
                    print("START BUTTON PRESSED")

            #----- COMBINATIONS -----

            # ---- STEERING WHEEL MOVEMENT ----
            # basic mouse movement
            if event.code == 'ABS_X':
                radian_val = abs_x_to_relative_radians(int(event.state))
                X_POS, Y_POS = radians_to_mouse_position(radian_val)
                pyautogui.moveTo(X_POS, Y_POS)
                print(f"Mouse moved to: ({X_POS}, {Y_POS}) with radians: {radian_val}")

if __name__ == "__main__":
    main()

# print('START TYPIUNG')
# time.sleep(2)  # Wait for 2 seconds before starting
# # for i in range(100):
