from inputs import get_gamepad
import pyautogui
import pydirectinput
import time
import math
import sounddevice as sd
import soundfile as sf
import threading
from queue import Queue

from mouse_inputs import GameScreenMouse


class ButtonHandler(GameScreenMouse):
    def __init__(self):
        '''
        MAKING ABS_HAT0X -1 ABS_HAT0Y -1 -> ABS_HAT0X_LEFT AND ABS_HAT0Y_UP
        MAKING ABS_HAT0X 1 ABS_HAT0Y 1 -> ABS_HAT0X_RIGHT AND ABS_HAT0Y_DOWN
        '''
        self.button_combos = self._set_button_combos()
        self.single_button_combos = self._set_single_button_combos()

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

        threading.Thread(target=flame_macro_thread, daemon=True).start()

    def play_horn_sound(self):
        """Play a horn sound when the ping button is pressed."""
        # Load audio file
        data, fs = sf.read('./Audio/test_horn.mp3')

        # Play non-blocking
        sd.play(data, fs)

    def button_press(self, button, key_down=False):
        def button_press_thread():
            """Press the button."""
            pydirectinput.press(button)

        threading.Thread(target=button_press_thread, daemon=True).start()

    def multi_button_press(self, button):
        def multi_button_press_thread():
            """Press multiple buttons in sequence."""
            pydirectinput.keyDown('ctrl')
            pydirectinput.press(button)
            pydirectinput.keyUp('ctrl')
        
        threading.Thread(target=multi_button_press_thread, daemon=True).start()

    # making all button mappings
    def _set_button_combos(self):
        combos = {
            # Triple combos
            ('BTN_TL', 'BTN_SELECT', 'BTN_START') : lambda: self.button_press('space'),
            ('BTN_THUMBL', 'BTN_SELECT', 'BTN_START') : self.swap_offset_side,

            # Double combos
            ('BTN_TL', 'BTN_THUMBL'): lambda: self.click_mouse(button='left'),
            ('BTN_TL', 'BTN_TR'): lambda: self.button_press('`'),
            ('BTN_TL', 'BTN_NORTH'): lambda: self.button_press('d'),
            ('BTN_TL', 'BTN_EAST'): lambda: self.button_press('f'),

            ('BTN_THUMBL', 'BTN_SOUTH'): lambda: self.multi_button_press('q'),
            ('BTN_THUMBL', 'BTN_NORTH'): lambda: self.multi_button_press('w'),
            ('BTN_THUMBL', 'BTN_EAST'): lambda: self.multi_button_press('e'),
            ('BTN_THUMBL', 'BTN_WEST'): lambda: self.multi_button_press('r'),

            # TODO: need a way to register difference between ABS_HAT0X -1 and 1
            # ('BTN_THUMBR', 'ABS_HAT0X'): lambda: self.button_press('2'),
            # ('BTN_THUMBR', 'ABS_HAT0Y'): lambda: self.button_press('3'),
        }
        return combos

    def _set_single_button_combos(self):
        combos = {
            'BTN_TR': lambda: self.click_mouse(button='right'),
            
            'BTN_WEST': lambda: self.button_press('q'),
            'BTN_NORTH': lambda: self.button_press('w'),
            'BTN_EAST': lambda: self.button_press('e'),
            'BTN_SOUTH': lambda: self.button_press('r'),
        }
        return combos


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
        self.debounce_time = 0.05  # 50ms debounce
        
        # Combo tracking
        self.combo_timeout = 0.5  # 500ms combo window
        self.active_combos = {}
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Track executed combos to prevent spam
        self.executed_combos = set()
        self.last_combo_time = {}

    def is_button_pressed(self, button):
        """Check if a button is currently pressed."""
        with self.lock:
            return button in self.pressed_buttons

    def was_button_just_pressed(self, button):
        """Check if a button was just pressed (edge detection)."""
        with self.lock:
            return ((self.current_event.get(button, 0) == 1 or 
                     self.current_event.get(button, 0) == -1) and
                    self.previous_event.get(button, 0) == 0)

    def was_button_just_released(self, button):
        """Check if a button was just released (edge detection)."""
        with self.lock:
            return (self.current_event.get(button, 0) == 0 and 
                    (self.previous_event.get(button, 0) == 1 or
                     self.previous_event.get(button, 0) == -1))

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

        # Handle different button states
        if state == 1 or state == -1:  # Button pressed
            if button not in self.pressed_buttons:
                self.pressed_buttons.add(button)
                self.button_press_times[button] = current_time
                
        elif state == 0:  # Button released
            if button in self.pressed_buttons:
                self.pressed_buttons.remove(button)
                self.button_release_times[button] = current_time
                
                # Clear executed combo when buttons are released
                current_combo = tuple(sorted(self.pressed_buttons))
                if current_combo in self.executed_combos:
                    self.executed_combos.remove(current_combo)

    def get_active_combo(self):
        """Get the currently active button combination."""
        with self.lock:
            # Sort pressed buttons for consistent combo detection
            combo = tuple(sorted(self.pressed_buttons))
            return combo if len(combo) > 1 else None

    def get_single_pressed_button(self):
        """Get single pressed button if only one is pressed."""
        with self.lock:
            if len(self.pressed_buttons) == 1:
                return next(iter(self.pressed_buttons))
            return None

    def execute_combo_action(self, combo):
        """Execute action based on button combination."""
        current_time = time.time()
        
        # Prevent spam - only execute once per combo press
        if combo in self.executed_combos:
            return False
            
        # Check if combo exists
        if combo in self.button_combos:
            self.button_combos[combo]()
            self.executed_combos.add(combo)
            self.last_combo_time[combo] = current_time
            return True
        return False

    def execute_single_action(self, button):
        """Execute single button action."""
        if button in self.single_button_combos:
            self.single_button_combos[button]()
            return True
        return False

    def read(self):
        """Read controller input - designed to be called from separate thread."""
        try:
            events = get_gamepad()
            
            with self.lock:
                # Store previous state for edge detection
                self.previous_event = self.current_event.copy()

                for event in events:
                    # Update current event state
                    self.current_event[event.code] = event.state
                      
                    # Update button state tracking for digital buttons
                    if event.ev_type == 'Key':
                        self.update_button_state(event.code, event.state)

            return self.current_event
        except Exception as e:
            print(f"Controller read error: {e}")
            return self.current_event

    def get_action(self):
        """Check for and execute controller actions - called from main loop."""
        with self.lock:
            # Check for active combos first (higher priority)
            active_combo = self.get_active_combo()
            if active_combo:
                if self.execute_combo_action(active_combo):
                    return
            
            # Check for single button actions (only if no combo active)
            if not active_combo:
                # Check for button press events
                for button in self.current_event:
                    if self.was_button_just_pressed(button):
                        if self.execute_single_action(button):
                            break  # Only execute one action per frame

    def get_current_state(self):
        """Get current controller state (thread-safe)."""
        with self.lock:
            return self.current_event.copy()

    def get_pressed_buttons(self):
        """Get currently pressed buttons (thread-safe)."""
        with self.lock:
            return self.pressed_buttons.copy()

    def get_changes(self):
        """Get only the values that changed between current and previous state."""
        with self.lock:
            changes = {key: self.current_event[key] 
                      for key in self.current_event 
                      if self.current_event[key] != self.previous_event[key]}
            return changes


if __name__ == "__main__":
    controller = Controller()
    
    def read_controller_thread(controller):
        while True:
            controller.read()
            time.sleep(0.001)  # Small sleep to prevent excessive CPU usage
    
    # Start the controller reading thread
    temp = threading.Thread(target=read_controller_thread, args=(controller,))
    temp.daemon = True
    temp.start()
    
    try:
        while True:
            # Get actions from controller
            controller.get_action()
            
            # Example usage
            if controller.current_event['BTN_NORTH'] == 1:
                controller._center_mouse()
                print("Centering mouse...")
            
            # Show only changes to reduce spam
            changes = controller.get_changes()
            if changes:
                print(f"Changes: {changes}")
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nShutting down...")