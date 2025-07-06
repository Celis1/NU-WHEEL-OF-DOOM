from inputs import get_gamepad
import pyautogui
import pydirectinput
import time
import math
import sounddevice as sd
import soundfile as sf
import threading
from collections import defaultdict

from mouse_inputs import GameScreenMouse

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
        
        # Previous state for edge detection
        self.previous_event = self.current_event.copy()
        
        # N-Key Rollover: Track all currently pressed buttons
        self.pressed_buttons = set()
        
        # Anti-ghosting: Track button press/release events with timestamps
        self.button_press_times = {}
        self.button_release_times = {}
        
        # Debounce settings (in seconds)
        self.debounce_time = 0.05  # 50ms debounce
        
        # Action queue for handling multiple simultaneous actions
        self.action_queue = []
        self.action_lock = threading.Lock()
        
        # Combo tracking
        self.combo_timeout = 0.5  # 500ms combo window
        self.active_combos = {}

    def flame_macro(self):
        def flame_macro_thread():
            """Simulate a series of key presses for the all chat flame macro."""
            basic_text = 'your ass is grass and imma mow it'

            # Press Shift + Enter using pydirectinput
            pydirectinput.keyDown('shift')
            pydirectinput.press('enter')
            pydirectinput.keyUp('shift')
            
            time.sleep(0.1)
            
            # Type the text
            pyautogui.write(basic_text)
            
            time.sleep(0.2)
            pydirectinput.press('enter')

        threading.Thread(target=flame_macro_thread).start()

    def play_horn_sound(self):
        """Play a horn sound when the ping button is pressed."""
        # Load audio file
        data, fs = sf.read('./Audio/test_horn.mp3')

        # Play non-blocking
        sd.play(data, fs)

    def is_button_pressed(self, button):
        """Check if a button is currently pressed."""
        return button in self.pressed_buttons

    def was_button_just_pressed(self, button):
        """Check if a button was just pressed (edge detection)."""
        return (self.current_event.get(button, 0) == 1 and 
                self.previous_event.get(button, 0) == 0)

    def was_button_just_released(self, button):
        """Check if a button was just released (edge detection)."""
        return (self.current_event.get(button, 0) == 0 and 
                self.previous_event.get(button, 0) == 1)

    def is_debounced(self, button):
        """Check if enough time has passed since last button event to avoid bouncing."""
        current_time = time.time()
        
        # Check press debounce
        if button in self.button_press_times:
            if current_time - self.button_press_times[button] < self.debounce_time:
                return False
        
        # Check release debounce
        if button in self.button_release_times:
            if current_time - self.button_release_times[button] < self.debounce_time:
                return False
        
        return True

    def update_button_state(self, button, state):
        """Update button state with anti-ghosting and debouncing."""
        current_time = time.time()
        
        # Anti-ghosting: ignore rapid state changes
        if not self.is_debounced(button):
            return
        
        if state == 1:  # Button pressed
            if button not in self.pressed_buttons:
                self.pressed_buttons.add(button)
                self.button_press_times[button] = current_time
                
        elif state == 0:  # Button released
            if button in self.pressed_buttons:
                self.pressed_buttons.remove(button)
                self.button_release_times[button] = current_time

    def get_active_combo(self):
        """Get the currently active button combination."""
        # Sort pressed buttons for consistent combo detection
        combo = tuple(sorted(self.pressed_buttons))
        return combo if len(combo) > 1 else None

    def execute_combo_action(self, combo):
        """Execute action based on button combination."""
        # Define combo mappings
        combo_actions = {
            ('BTN_TL', 'BTN_THUMBR'): self.handle_mouse_combo,
            ('BTN_TL', 'BTN_THUMBL'): lambda: self.click_mouse(button='left'),
            ('BTN_TL', 'BTN_TR'): lambda: self.button_press('`'),
            ('BTN_TL', 'BTN_NORTH'): lambda: self.button_press('d'),
            ('BTN_TL', 'BTN_EAST'): lambda: self.button_press('f'),
        }
        
        if combo in combo_actions:
            combo_actions[combo]()
            return True
        return False

    def handle_mouse_combo(self):
        """Handle mouse movement combos with directional input."""
        # Check for directional input while mouse combo is active
        if self.current_event.get('ABS_HAT0Y') == -1:
            self.absolute_mouse_move()
        elif self.current_event.get('ABS_HAT0Y') == 1:
            self.absolute_mouse_move()
        elif self.current_event.get('ABS_HAT0X') == 1:
            self.absolute_mouse_move()
        elif self.current_event.get('ABS_HAT0X') == -1:
            self.absolute_mouse_move()

    def add_action_to_queue(self, action):
        """Add an action to the queue for execution."""
        with self.action_lock:
            self.action_queue.append(action)

    def process_action_queue(self):
        """Process all queued actions."""
        with self.action_lock:
            while self.action_queue:
                action = self.action_queue.pop(0)
                try:
                    action()
                except Exception as e:
                    print(f"Error executing action: {e}")

    def read(self):
        """Read gamepad events with enhanced state tracking."""
        events = get_gamepad()
        
        # Store previous state for edge detection
        self.previous_event = self.current_event.copy()
        
        # Process all events
        for event in events:
            self.current_event[event.code] = event.state
            
            # Update button state tracking for digital buttons
            if event.code.startswith('BTN_'):
                self.update_button_state(event.code, event.state)

        return self.current_event
    
    def button_press(self, button, key_down=False):
        def button_press_thread():
            """Press the button."""
            pydirectinput.press(button)

        threading.Thread(target=button_press_thread).start()

    def multi_button_press(self, button):
        def multi_button_press_thread():
            """Press multiple buttons in sequence."""
            pydirectinput.keyDown('ctrl')
            pydirectinput.press(button)
            pydirectinput.keyUp('ctrl')
        
        threading.Thread(target=multi_button_press_thread).start()

    def get_action(self):
        """Enhanced action processing with N-key rollover and anti-ghosting."""
        
        # Process any queued actions first
        self.process_action_queue()
        
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
                
    def handle_single_button_press(self, button):
        """Handle individual button press events."""
        single_button_actions = {
            'BTN_START': lambda: self.button_press('escape'),
            'BTN_SELECT': lambda: self.button_press('tab'),
            'BTN_SOUTH': lambda: self.button_press('space'),
            'BTN_WEST': lambda: self.button_press('r'),
            # Add more single button mappings as needed
        }
        
        if button in single_button_actions:
            # Queue the action to prevent blocking
            self.add_action_to_queue(single_button_actions[button])

    def cleanup_old_states(self):
        """Clean up old button state data to prevent memory leaks."""
        current_time = time.time()
        cleanup_threshold = 60  # 1 minute
        
        # Clean up old press times
        old_press_keys = [k for k, v in self.button_press_times.items() 
                         if current_time - v > cleanup_threshold]
        for key in old_press_keys:
            del self.button_press_times[key]
            
        # Clean up old release times
        old_release_keys = [k for k, v in self.button_release_times.items() 
                           if current_time - v > cleanup_threshold]
        for key in old_release_keys:
            del self.button_release_times[key]

    def get_pressed_buttons_info(self):
        """Debug method to see currently pressed buttons."""
        return {
            'pressed_buttons': list(self.pressed_buttons),
            'active_combo': self.get_active_combo(),
            'queue_length': len(self.action_queue)
        }