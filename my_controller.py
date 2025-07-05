

from inputs import get_gamepad
import pyautogui
import pydirectinput
import time
import math
import sounddevice as sd
import soundfile as sf
import threading

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
        
        # self.previous_event = self.current_event.copy()

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

    def read(self):
        events = get_gamepad()
        for event in events:
            # if event.ev_type == 'Absolute' or event.ev_type == 'Key':
            self.current_event[event.code] = event.state

        return self.current_event
    
    def button_press(self, button):
        def button_press_thread():
            """Press the button."""
            pydirectinput.press(button)
        """Simulate a button press."""
        threading.Thread(target=button_press_thread).start()

    def multi_button_press(self, button):
        def multi_button_press_thread():
            """Press multiple buttons in sequence."""
            pydirectinput.keyDown('ctrl')
            pydirectinput.press(button)
            pydirectinput.keyUp('ctrl')

        """Simulate a multi-button press."""
        threading.Thread(target=multi_button_press_thread).start()


    def get_action(self):
        
        # --------- COMBOS WITH FRONT L ---------
        if self.current_event['BTN_TL'] == 1:
            if self.current_event['BTN_NORTH'] == 1:
                self.button_press('d')
                # return 'FLASH'
            
            elif self.current_event['BTN_EAST'] == 1:
                self.button_press('f')
                # return 'SMITE'

            elif self.current_event['BTN_SOUTH'] == 1:
                self.button_press('s')
                # return 'STOP_MOVING'

            elif self.current_event['BTN_WEST'] == 1:
                self.button_press('4')
                # return 'WARD_SLOT'

        # --------- COMBOS WITH FRONT R ---------
        if self.current_event['BTN_TL'] == 1:
            if self.current_event['ABS_HAT0X'] == -1:
                self.button_press('1')
            elif self.current_event['ABS_HAT0Y'] == -1:
                self.button_press('2')
            elif self.current_event['ABS_HAT0X'] == 1:
                self.button_press('3')
            elif self.current_event['ABS_HAT0Y'] == 1:
                self.button_press('4')

        # --------- COMBOS WITH BACK R ---------
        if self.current_event['BTN_THUMBR'] == 1:
            if self.current_event['ABS_HAT0X'] == -1:
                # return 'mouse_left'
                pass
            
            elif self.current_event['ABS_HAT0X'] == 1:
                # return 'mouse_right'
                pass
            
            elif self.current_event['ABS_HAT0Y'] == -1:
                # self.center_mouse()
                pass
                # return 'mouse_up'

            elif self.current_event['ABS_HAT0Y'] == 1:
                # return 'mouse_down'
                pass

        # --------- COMBOS WITH BACK L ---------
        if self.current_event['BTN_THUMBL'] == 1:
            if self.current_event['BTN_NORTH'] == 1:
                self.multi_button_press('q')

            elif self.current_event['BTN_EAST'] == 1:
                self.multi_button_press('e')

            elif self.current_event['BTN_SOUTH'] == 1:
                self.multi_button_press('r')

            elif self.current_event['BTN_WEST'] == 1:
                self.multi_button_press('d')

        # --------- PADDLES ---------
        if self.current_event['BTN_TL'] == 1:
            # self.center_mouse()
            pass
        
        if self.current_event['BTN_TR'] == 1:
            self.click_mouse(button='right')

        # --------- BUTTONS ---------
        if self.current_event['BTN_NORTH'] == 1:
            self.button_press('w')
        
        if self.current_event['BTN_SOUTH'] == 1:
            self.button_press('q')
        
        if self.current_event['BTN_EAST'] == 1:
            self.button_press('e')
        
        if self.current_event['BTN_WEST'] == 1:
            self.button_press('r')

        # --------- TRIGGERS ---------
        if self.current_event['ABS_RZ'] != 0:
            inc_val = self.current_event['ABS_RZ'] // 10  # Scale to a reasonable increment
            self.grow_radius(inc_val)
            # return 'enlarge_circle_radius'
        if self.current_event['ABS_Z'] != 0:
            dec_value = self.current_event['ABS_Z'] // 10 # Scale to a reasonable decrement
            self.shrink_radius(dec_value)
            # return 'reduce_circle_radius'

        # --------- WINDOWS BUTTONS ---------
        if self.current_event['BTN_SELECT'] == 1:
            # play the horn sound
            self.play_horn_sound()
            self.button_press('u')  # ping omw button
            
            # return 'ping_horn'
        if self.current_event['BTN_START'] == 1:
            # return 'all_chat_flame_macro'
            print("All chat flame macro triggered")
            self.flame_macro()