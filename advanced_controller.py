

from inputs import get_gamepad
import pyautogui
import pydirectinput
import time
import sounddevice as sd
import soundfile as sf
import threading
from queue import Queue


from mouse_inputs import GameScreenMouse

class Controller(ButtonHandler):
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
        
        self.previous_event = self.current_event.copy()

        # N-Key Rollover: Track all currently pressed buttons
        self.pressed_buttons = set()
        
        # Anti-ghosting: Track button press/release events with timestamps
        self.button_press_times = {}
        self.button_release_times = {}
        
        # Debounce settings (in seconds)
        self.debounce_time = 0.005  #debounce
        
        # queue of actions
        self.action_queue = []
        
        # Combo tracking
        self.combo_timeout = 0.05  #combo window
        self.active_combos = {}

    # def is_button_pressed(self, button):
    #     """Check if a button is currently pressed."""
    #     return button in self.pressed_buttons

    # def was_button_just_pressed(self, button):
    #     """Check if a button was just pressed (edge detection)."""
    #     return ((self.current_event.get(button, 0) == 1 or 
    #              self.current_event.get(button, 0) == -1) and
    #             self.previous_event.get(button, 0) == 0)

    # def was_button_just_released(self, button):
    #     """Check if a button was just released (edge detection)."""
    #     return (self.current_event.get(button, 0) == 0 and 
    #             (self.previous_event.get(button, 0) == 1 or
    #              self.previous_event.get(button, 0) == -1))

    # def is_debounced(self, button):
    #     """Check if enough time has passed since last button event to avoid bouncing."""
    #     current_time = time.time()
        
    #     # Check press debounce
    #     if button in self.button_press_times:
    #         if current_time - self.button_press_times[button] < self.debounce_time:
    #             return False
        
    #     # Check release debounce
    #     if button in self.button_release_times:
    #         if current_time - self.button_release_times[button] < self.debounce_time:
    #             return False
        
    #     return True
    
    def update_button_state(self, button, state):
        """Update button state with anti-ghosting and debouncing."""
        current_time = time.time()
        
        # Anti-ghosting: ignore rapid state changes
        if not self.is_debounced(button):
            print(f"Button {button} state change ignored due to debounce.")
            return

        # TODO : ABS_HAT0X AND ABS_HAT0Y BOTH HAVE -1 VALUES WE CANT ADD THE SAME NAME TO THE SET
        if state == 1 or state == -1:  # Button pressed
            if button not in self.pressed_buttons:
                self.pressed_buttons.add(button)
                self.button_press_times[button] = current_time
                
        elif state == 0:  # Button released
            if button in self.pressed_buttons:
                self.pressed_buttons.remove(button)
                self.button_release_times[button] = current_time

        

    # def get_active_combo(self):
    #     """Get the currently active button combination."""
    #     # Sort pressed buttons for consistent combo detection
    #     combo = tuple(sorted(self.pressed_buttons))
        
    #     # TODO: WE MIGHT JUST RETURN THE COMBO WITH SINGLE BUTTONS
    #     return combo if len(combo) > 1 else None


    def execute_combo_action(self, combo):
        """Execute action based on button combination."""
        
        if combo in self.button_combos:
            self.button_combos[combo]()
            return True
        return False
    
    def handle_single_button_press(self, button):
        """Handle individual button press events."""
        
        if button in self.single_button_combos:
            # Queue the action to prevent blocking
            self.action_queue.append(self.single_button_combos[button])

    def read(self):
        events = get_gamepad()

        # Store previous state for edge detection
        self.previous_event = self.current_event.copy()

        for event in events:
            # if event.ev_type == 'Absolute' or event.ev_type == 'Key':
            self.current_event[event.code] = event.state
              
            # Update button state tracking for digital buttons
            if event.ev_type == 'Key':
                self.update_button_state(event.code, event.state)

        return self.current_event
    

    def get_action(self):
        # Process queued actions first 
        if self.action_queue:
            action = self.action_queue.pop(0)
            action()
        
        # Check for active combos (N-key rollover)
        active_combo = self.get_active_combo()
        if active_combo:
            if self.execute_combo_action(active_combo):
                return
        
        # Handle individual button presses (with edge detection to prevent spam)
        for button in ['BTN_TL', 'BTN_TR', 'BTN_NORTH', 'BTN_EAST', 'BTN_SOUTH', 
                       'BTN_WEST', 'BTN_THUMBL', 'BTN_THUMBR', 'BTN_START', 'BTN_SELECT']:
            if self.was_button_just_pressed(button):
                self.handle_single_button_press(button)
        

    # DEBUGGING METHOD
    def get_pressed_buttons_info(self):
        """Debug method to see currently pressed buttons."""
        return {
            'pressed_buttons': list(self.pressed_buttons),
            'active_combo': self.get_active_combo(),
            'queue_length': len(self.action_queue)
        }

if __name__ == "__main__":
    controller = Controller()
    
    while 1:
        events = controller.read()
        # if controller.current_event['BTN_NORTH'] == 1:
        #     controller._center_mouse()
        #     print("Centering mouse...")
        print(controller.get_pressed_buttons_info())