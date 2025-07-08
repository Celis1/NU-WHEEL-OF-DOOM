

from inputs import get_gamepad
import pyautogui
import pydirectinput
import time
import math
import sounddevice as sd
import soundfile as sf
import threading

from mouse_inputs import GameScreenMouse


class AdvancedControlFunc:
    pass


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

        # TODO: change the later ifs into elifs because we dont want to trigger multiple actions at once
        # TODO: WE GOTTA FIND A BETTER SOLUTION THAN 1000000 RETURNS

        # --------- COMBOS PADDLE L ---------
        if self.current_event['BTN_TL'] == 1:
            
            if self.current_event['BTN_THUMBR'] == 1:
                if self.current_event['ABS_HAT0Y'] == -1:
                    self.absolute_mouse_move()
                    return
                elif self.current_event['ABS_HAT0Y'] == 1:
                    self.absolute_mouse_move()
                    return
                elif self.current_event['ABS_HAT0X'] == 1:
                    self.absolute_mouse_move()
                    return
                elif self.current_event['ABS_HAT0X'] == -1:
                    self.absolute_mouse_move()
                    return


            elif self.current_event['BTN_THUMBL'] ==1:
                self.click_mouse(button='left')
                return

            elif self.current_event['BTN_TR'] == 1:
                self.button_press('`')
                return

            elif self.current_event['BTN_NORTH'] == 1:
                self.button_press('d')
                return

            elif self.current_event['BTN_EAST'] == 1:
                self.button_press('f')
                return

            # TODO: CHANGE VIEW ALLY MACRO
            # elif self.current_event['ABS_HAT0Y'] == -1:
            #     self.button_press('f2')
            #     if self.current_event['BTN_SELECT'] == 1:
            #         self.button_press('k')
            
            # elif self.current_event['ABS_HAT0X'] == 1:
            #     self.button_press('f3')
            #     if self.current_event['BTN_SELECT'] == 1:
            #         self.button_press('k')

            # elif self.current_event['ABS_HAT0Y'] == 1:
            #     self.button_press('f4')
            #     if self.current_event['BTN_SELECT'] == 1:
            #         self.button_press('k')

            # elif self.current_event['ABS_HAT0X'] == -1:
            #     self.button_press('f5')
            #     if self.current_event['BTN_SELECT'] == 1:
            #         self.button_press('k')


        # --------- COMBOS BACK L ---------
        if self.current_event['BTN_THUMBL'] == 1:

            # combos with BACK R
            if self.current_event['BTN_THUMBR'] == 1:
                if self.current_event['ABS_RZ'] != 0:
                    self.set_radius_max()
                    return
                
                elif self.current_event['ABS_Z'] != 0:
                    self.set_radius_min()
                    return


            if self.current_event['BTN_SOUTH'] == 1:
                self.multi_button_press('r')
                return

            elif self.current_event['BTN_NORTH'] == 1:
                self.multi_button_press('w')
                return

            elif self.current_event['BTN_EAST'] == 1:
                self.multi_button_press('e')
                return

            elif self.current_event['BTN_WEST'] == 1:
                self.multi_button_press('q')
                return
                

            elif self.current_event['ABS_HAT0X'] == 1:
                if self.current_event['BTN_THUMBR'] == 1:
                    self.multi_button_press(4)
                    return
                else:
                    # TODO: WE WANT SHIFT CLICK FUNCTION
                    self.button_press('`')
                    return

            elif self.current_event['ABS_HAT0Y'] == -1:
                if self.current_event['BTN_THUMBR'] == 1:
                    self.button_press('t')
                    return
                else:
                    self.button_press('o')
                    return
            
            elif self.current_event['ABS_HAT0X'] == -1:
                self.button_press('p')
                return
            
            elif self.current_event['ABS_HAT0Y'] == 1:
                self.button_press('b')
                return

        # --------- COMBOS BACK R ---------
        if self.current_event['BTN_THUMBR'] == 1:
            if self.current_event['ABS_HAT0X'] == 1:
                self.button_press('2')
                return

            elif self.current_event['ABS_HAT0Y'] == 1:
                self.button_press('3')
                return

            elif self.current_event['ABS_HAT0X'] == -1:
                self.button_press('4')
                return
            
            elif self.current_event['ABS_HAT0Y'] == -1:
                self.button_press('s')
                return

        # --------- CORE BUTTONS ---------
        elif self.current_event['BTN_TR'] == 1:
            self.click_mouse(button='right')
            return

        elif self.current_event['BTN_SOUTH'] == 1:
            self.button_press('r')
            return
        elif self.current_event['BTN_NORTH'] == 1:
            self.button_press('w')
            return
        elif self.current_event['BTN_EAST'] == 1:
            self.button_press('e')
            return
        elif self.current_event['BTN_WEST'] == 1:
            self.button_press('q')
            return

        # --------- DPAD ---------
        elif self.current_event['ABS_HAT0Y'] == -1:
            self.quarter_step_mouse('N')
            return
        elif self.current_event['ABS_HAT0Y'] == 1:
            self.quarter_step_mouse('S')
            return
        elif self.current_event['ABS_HAT0X'] == 1:
            self.quarter_step_mouse('E')
            return
        elif self.current_event['ABS_HAT0X'] == -1:
            self.quarter_step_mouse('W')
            return

        # play the horn sound
        elif self.current_event['BTN_SELECT'] == 1:
            if self.current_event['BTN_THUMBL'] == 1:
                if self.current_event['BTN_START'] == 1:
                    print("Swapping offset side")
                    self.swap_offset_side()
                    return
                
            elif self.current_event['BTN_TL'] == 1:
                if self.current_event['BTN_START'] == 1:
                    print('UNLOCKING CAMERA')
                    self.button_press('space')
                    return
            else:
                self.play_horn_sound()
                self.button_press('u')
                return

        # flame macro
        elif self.current_event['BTN_START'] == 1:
            print("All chat flame macro triggered")
            self.flame_macro()
            return
        
        # --- triggers ---
        if self.current_event['ABS_RZ'] != 0:
            inc_val = self.current_event['ABS_RZ'] // 30  # Scale to a reasonable increment
            self.grow_radius(inc_val)
            return
           
        if self.current_event['ABS_Z'] != 0:
            dec_value = self.current_event['ABS_Z'] // 30 # Scale to a reasonable decrement
            self.shrink_radius(dec_value)
            return


if __name__ == "__main__":
    controller = Controller()
    
    while 1:
        events = controller.read()
        if controller.current_event['BTN_NORTH'] == 1:
            controller._center_mouse()
            print("Centering mouse...")

