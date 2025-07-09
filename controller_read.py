

from inputs import get_gamepad
import pyautogui
import pydirectinput
import time
import sounddevice as sd
import soundfile as sf
import threading


from mouse_inputs import GameScreenMouse


class Abilitys(GameScreenMouse):

    def __init__(self):
        # ALPHATIVE ORDER OF BTN PRESS
        self.ignore_brake = 0
        self.ignore_gas = 0
        self.ignore_count = 100

        self.abilties = {
            # Clicks
            ('BTN_TR',): lambda: self.click_mouse(button='right'),
            ('BTN_THUMBL', 'BTN_TL'): lambda: self.click_mouse(button='left'),
            ('BTN_TL', 'BTN_TR'): lambda: self.button_press('`'),

            # core abilites
            ('BTN_WEST',): lambda: self.button_press('q'),
            ('BTN_NORTH',): lambda: self.button_press('w'),
            ('BTN_EAST',): lambda: self.button_press('e'),
            ('BTN_SOUTH',): lambda: self.button_press('r'),
            ('BTN_NORTH', 'BTN_TL'): lambda: self.button_press('d'),
            ('BTN_EAST','BTN_TL', ): lambda: self.button_press('f'),

            # lvl abilites
            ('BTN_THUMBL', 'BTN_WEST'): lambda: self.multi_button_press('q'),
            ('BTN_NORTH', 'BTN_THUMBL' ): lambda: self.multi_button_press('w'),
            ('BTN_EAST', 'BTN_THUMBL' ): lambda: self.multi_button_press('e'),
            ('BTN_SOUTH', 'BTN_THUMBL'): lambda: self.multi_button_press('r'),

            # items
            ('ABS_HAT0X_RIGHT', 'BTN_TL'): lambda: self.button_press('2'),
            ('ABS_HAT0Y_DOWN', 'BTN_TL'): lambda: self.button_press('3'),
            ('ABS_HAT0X_LEFT', 'BTN_TL'): lambda: self.button_press('4'),

            # movement
            ('ABS_HAT0Y_UP', 'BTN_TL'): lambda: self.button_press('s'),

            # ping
            ('BTN_SELECT',): lambda: self.button_press('u'),

            # misc actions
            ('ABS_HAT0Y_UP', 'BTN_THUMBL'): lambda: self.button_press('o'),
            ('ABS_HAT0X_LEFT', 'BTN_THUMBL'): lambda: self.button_press('p'),
            ('ABS_HAT0Y_DOWN', 'BTN_THUMBL'): lambda: self.button_press('b'),

            # view ally!
            # TODO: ADD ALLY VIEW MACRO
            ('ABS_HAT0Y_UP', 'BTN_THUMBR'): lambda: self.button_press('f2'),
            ('ABS_HAT0X_RIGHT', 'BTN_THUMBR'): lambda: self.button_press('f3'),
            ('ABS_HAT0Y_DOWN', 'BTN_THUMBR'): lambda: self.button_press('f4'),
            ('ABS_HAT0X_LEFT', 'BTN_THUMBR'): lambda: self.button_press('f5'),


            ('BTN_TL', 'BTN_SELECT', 'BTN_START') : lambda: self.button_press('space'),
            ('BTN_SELECT', 'BTN_START', 'BTN_THUMBL') : self.swap_offset_side,

            # mouse motions
            ('BTN_SELECT', 'BTN_START') : lambda: self.button_press('space'),
            # ('BTN_THUMBL', 'BTN_SELECT', 'BTN_START') : self.swap_offset_side,

            # --------- DPAD ---------
            ('ABS_HAT0Y_UP',): lambda: self.quarter_step_mouse('N'),
            ('ABS_HAT0Y_DOWN',): lambda: self.quarter_step_mouse('S'),
            ('ABS_HAT0X_LEFT',): lambda: self.quarter_step_mouse('W'),
            ('ABS_HAT0X_RIGHT',): lambda: self.quarter_step_mouse('E'),


            # offset
            ('BTN_THUMBL', 'BTN_THUMBR', 'BTN_TL', 'BTN_TR'): self.shop_offset,
            ('BTN_SELECT', 'BTN_START', 'BTN_THUMBL') : self.swap_offset_side,
            

    }
        
    def update_pedals(self):


        # gas pedal
        gas_val = self.buttons['ABS_RZ']
        # brake pedal
        break_val = self.buttons['ABS_Z']


        if gas_val != 0:
            # full throttle is max radius
            if self.buttons['ABS_RZ'] >= 255:
                self.set_radius_max()
            #     self.ignore_gas = 0

            # if self.ignore_gas < self.ignore_count:
            #     self.ignore_gas += 1
            #     return
            
            self.grow_radius(gas_val)
            
        
        if break_val != 0:

            # full brake is min radius
            if self.buttons['ABS_Z'] >= 255:
                self.set_radius_attack_range()
                self.ignore_brake = 0


            if self.ignore_brake < self.ignore_count:
                if self.ignore_brake < self.ignore_count:
                    self.ignore_brake += 1
                    return
                
            self.shrink_radius(break_val)
                
        elif break_val == 0:
            # if the brake is released, we reset the ignore brake counter
            self.ignore_brake = self.ignore_count
                
            
            
    
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
        # tracking buttons
        self.btn_active = set()
        self.btn_press_times = {}

        # dpad variables
        self.x_plus = False
        self.y_plus = False

        # n-key rollover anti ghosting
        self.debounce_time = 0.05  # 1ms debounce time
        self.combo_timeout = 0.1  #combo window ms
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

        # we want to read the buttons change in its state and value and record when it was pressed
        current_time = time.time()

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
    

    def update_btns_active(self, btn_name, btn_value, current_time, dpad_btn=False):

        curr_btn_name = btn_name

        # getting dpad stuff
        if dpad_btn:
            curr_btn_name = self.get_dpad_direction_name(btn_name)
            print(f'WORKIGN WITH ------ D-Pad button: {btn_name} with value: {btn_value}')

        print('CURRENT BUTTON NAME:', curr_btn_name)
        # check if the value is 0, if so we remove it from the queue
        if btn_value == 0:
            if curr_btn_name in self.btn_active:
                self.btn_active.remove(curr_btn_name)
                # self.curr_combo_time = 0
        
        else:
            self.curr_combo_time = current_time
            self.btn_active.add(curr_btn_name)

        return self.curr_combo_time
    
    def get_dpad_direction_name(self, btn_name):
        """Get the current direction of the D-Pad."""

        # button name is ABS_HAT0Y or ABS_HAT0X
        if btn_name == 'ABS_HAT0Y':
            
            if self.buttons[btn_name] == 0:
                if self.y_plus:
                    return 'ABS_HAT0Y_DOWN'
                else:
                    return 'ABS_HAT0Y_UP'
                
            elif self.buttons[btn_name] == 1:
                self.y_plus = True
                return 'ABS_HAT0Y_DOWN'
            
            elif self.buttons[btn_name] == -1:
                self.y_plus = False
                return 'ABS_HAT0Y_UP'
            
        elif btn_name == 'ABS_HAT0X':
            if self.buttons[btn_name] == 0:
                if self.x_plus:
                    return 'ABS_HAT0X_RIGHT'
                else:
                    return 'ABS_HAT0X_LEFT'
                
            elif self.buttons[btn_name] == 1:
                self.x_plus = True
                return 'ABS_HAT0X_RIGHT'
            
            elif self.buttons[btn_name] == -1:
                self.x_plus = False
                return 'ABS_HAT0X_LEFT'
            

    def get_pressed_buttons_info(self):
        """Return the current state of the buttons for debugging."""

        debug_str = f'Active Buttons: {self.btn_active},\nButton States: {self.buttons},\nCurrent Combo Time: {self.curr_combo_time:.3f}s'

        return debug_str
    


class Controller(ButtonBinding, Abilitys):
    def __init__(self):
        ButtonBinding.__init__(self)
        GameScreenMouse.__init__(self)
        Abilitys.__init__(self)

        self.action_queue = []

    def read(self):
        dpad_btn = False
        events = get_gamepad()

        for event in events:

            if event.ev_type == 'Key' or event.code == 'ABS_HAT0Y' or event.code == 'ABS_HAT0X':
                # recording that is t dpad with 3 inputs
                if event.code.startswith('ABS_'):
                    print(f'------>Dpad button was pressed: {event.code} with value: {event.state}')
                    dpad_btn = True

                # call out update function
                btns_if_pressed = self.incoming_btn(event.code, event.state)
                if isinstance(btns_if_pressed, tuple):
                    # unpack the tuple
                    btn_name, btn_value, curr_combo_time = btns_if_pressed

                    print('------READ A CHANGE TO DPAD ------')
                    self.update_btns_active(btn_name, btn_value, curr_combo_time, dpad_btn)

            elif event.ev_type == 'Absolute':
                self.buttons[event.code] = event.state

            
        # self.get_pressed_buttons_info()

    

    def update_action_queue(self):

        print('---Updating action queue----')

        if  len(self.btn_active) == 0:
            # if no buttons are active, we return
            print('no buttons active')
            return

        # Check if the current combo is still active
        if self.curr_combo_time < self.combo_timeout:
            print('--->combo timeout reached')
            # self.curr_combo_time = 0
            return
        
        print('active buttons', self.btn_active)

        print('sorting buttons')
        pressed_buttons = tuple(sorted(self.btn_active))

        print('checking abilityes')
        print('------>SORTED NAMES OF ABILTIES:', pressed_buttons)
        print(len(pressed_buttons))
        # now we want to queue the ability
        if len(pressed_buttons) > 0:
            # single button press
            func = self.abilties.get(pressed_buttons, None)
            
            if func:
                print('FOUND AN ACTION PLEZ GOD ------------>')
                print(f'Adding single press action: {pressed_buttons}')
                self.btn_active.clear()
                self.action_queue.append(func)
                print(f'Action Queue: {len(self.action_queue)}')

        

    def call_action(self):
        """Call the action from the queue."""
        # self.curr_combo_time = current_time


        self.update_action_queue()

        if len(self.action_queue) > 0:
            # if the action queue is empty, we return
            action = self.action_queue.pop(0)
            action()
            print(f'ACTION WAS CALLED')


