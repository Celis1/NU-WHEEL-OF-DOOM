

from inputs import get_gamepad
import pyautogui
import pydirectinput
import time
import sounddevice as sd
import soundfile as sf
import threading


from mouse_inputs import GameScreenMouse
class Abilitys:
    def triple_press(self):
        combos = {
            # Triple combos
            ('BTN_TL', 'BTN_SELECT', 'BTN_START') : lambda: self.button_press('space'),
            ('BTN_THUMBL', 'BTN_SELECT', 'BTN_START') : self.swap_offset_side,
        }

        return combos
    
    def double_press(self):
        combos = {
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

    def single_press(self):
        combos = {
            ('BTN_TR'): lambda: self.click_mouse(button='right'),
            
            ('BTN_WEST'): lambda: self.button_press('q'),
            ('BTN_NORTH'): lambda: self.button_press('w'),
            ('BTN_EAST'): lambda: self.button_press('e'),
            ('BTN_SOUTH'): lambda: self.button_press('r'),

        }
        return combos
        
    # ---- converting action to on screen effect ----
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




class ButtonBinding:

    def __init__(self):
        self.btn_active = set()
        self.btn_press_times = {}
        self.debounce_time = 0.005  # 5ms debounce time
        self.combo_timeout = 0.05  #combo window ms
        self.curr_combo_time = 0


        self.buttons = {
    
            'ABS_X': 0,
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
        


    def incoming_btn(self, btn_name, btn_value):

        # check if 
    
        # we want to read the buttons change in its state and value and record when it was pressed
        current_time = time.time()

        if self.btn_active in self.buttons:
            # if the button is already active, we ignore it
            return

        # check state change ignore No change 
        if btn_value == self.buttons[btn_name]:
            return  
        
        # check debounce time
        if btn_name in self.btn_press_times:
            last_press_time = self.btn_press_times[btn_name]
            if current_time - last_press_time < self.debounce_time:
                # If the buttons was pressed too recently, ignore this press
                return
        
        # now we record update the buttons state
        self.buttons[btn_name] = btn_value
        self.btn_press_times[btn_name] = current_time
        return (btn_name, btn_value, current_time)
    

    def update_btns_active(self, btn_name, btn_value, current_time):
        # check if the value is 0, if so we remove it from the queue
        if btn_value == 0:
            if btn_name in self.btn_active:
                self.btn_active.remove(btn_name)
        
        else:
            self.curr_combo_time = current_time
            self.btn_active.add(btn_name)

    def debugging_info(self):
        """Return the current state of the buttons for debugging."""
        return {
            'active_buttons': self.btn_active,
            'buttons dictionary': self.buttons,
        }




class Controller(ButtonBinding, GameScreenMouse, Abilitys):
    def __init__(self):
        ButtonBinding.__init__(self)
        GameScreenMouse.__init__(self)
        Abilitys.__init__(self)

        self.action_queue = []

    def read(self):
        events = get_gamepad()

        for event in events:

            if event.ev_type == 'Absolute':
                    self.buttons[event.code] = event.state
              
            # Update button state tracking for digital buttons
            if event.ev_type == 'Key' or event.code == 'ABS_HAT0Y' or event.code == 'ABS_HAT0X':
                # call out update function
                btns_if_pressed = self.incoming_btn(event.code, event.state)
                if isinstance(btns_if_pressed, tuple):
                    # unpack the tuple
                    btn_name, btn_value, current_time = btns_if_pressed
                    self.update_btns_active(btn_name, btn_value)

            
        self.queue_action()
        self.debugging_info()

    

    def queue_action(self):

        if not self.btn_active:
            # if no buttons are active, we return
            return

        # Check if the current combo is still active
        if self.curr_combo_time > self.combo_timeout:
            return

        
        pressed_buttons = tuple(sorted(self.btn_active))

        # now we want to queue the ability
        if len(pressed_buttons) == 1:
            # single button press
            if pressed_buttons in self.single_press():
                self.action_queue.append(self.single_press()[pressed_buttons])
        # elif len(values) == 2:
        #     # double button press
        #     if values in self.double_press():
        #         self.action_queue.append(self.double_press()[values])
        # elif len(values) == 3:
        #     # triple button press
        #     if values in self.triple_press():
        #         self.action_queue.append(self.triple_press()[values])


        self.action_queue.append(self.single_press()[pressed_buttons])
        self.btn_active.clear()  # Clear active buttons after queuing action


    def call_action(self):
        """Call the action from the queue."""
        if self.action_queue:
            action = self.action_queue.pop(0)
            action()
        