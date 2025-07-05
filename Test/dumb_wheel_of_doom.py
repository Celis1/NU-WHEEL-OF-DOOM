from inputs import get_gamepad
import pyautogui
import pydirectinput
import threading

current_event = {'ABS_X': 0,
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


def button_press(button):
    def press_button():
        """Press the button."""
        pydirectinput.press(button)
    """Simulate a button press."""
    threading.Thread(target=press_button).start()


def main():
    """Just print out some event infomation when the gamepad is used."""
    while 1:
        events = get_gamepad()
        for event in events:
            current_event[event.code] = event.state
            # print(event.ev_type, event.code, event.state)
            print(current_event)
            
            if current_event['BTN_TL'] == 1:
                if current_event['BTN_NORTH'] == 1:
                    pydirectinput.press('d')
                    # return 'FLASH'
                
                elif current_event['BTN_EAST'] == 1:
                    pydirectinput.press('f')
                    # return 'SMITE'

                elif current_event['BTN_SOUTH'] == 1:
                    pydirectinput.press('s')
                    # return 'STOP_MOVING'

                elif current_event['BTN_WEST'] == 1:
                    pydirectinput.press('4')
                    # return 'WARD_SLOT'qqq

            # [FRONT R: BTN_TR] + [D-PAD LEFT: ABS_HAT0X -1] = (q) item slot 1
            # [FRONT R: BTN_TR] + [D-PAD UP: ABS_HAT0Y -1] =  (e) item slot 2
            # [FRONT R: BTN_TR] + [D-PAD RIGHT: ABS_HAT0X 1] = (2) item slot 3
            # [FRONT R: BTN_TR] + [D-PAD DOWN: ABS_HAT0Y 1] = (mb5) ward slot

            if current_event['BTN_TR'] == 1:
                if current_event['ABS_HAT0X'] == -1:
                    pydirectinput.press('1')
                elif current_event['ABS_HAT0Y'] == -1:
                    pydirectinput.press('2')
                elif current_event['ABS_HAT0X'] == 1:
                    pydirectinput.press('3')
                # elif current_event['ABS_HAT0Y'] == 1:
                #     pydirectinput.press('4')

            # [BACK R: BTN_THUMBR] + D-PAD LEFT,RIGHT,UP,DOWN: MOUSE ABSOLUTE MOVEMENT
            if current_event['BTN_THUMBR'] == 1:
                if current_event['ABS_HAT0X'] == -1:
                    # return 'mouse_left'
                    pass
                
                elif current_event['ABS_HAT0X'] == 1:
                    # return 'mouse_right'
                    pass
                
                elif current_event['ABS_HAT0Y'] == -1:
                    # center_mouse()
                    pass
                    # return 'mouse_up'

                elif current_event['ABS_HAT0Y'] == 1:
                    # return 'mouse_down'
                    pass
                

            # LEFT PADDLE: BTN_TL = MOUSE CENTER
            # RIGHT PADDLE: BTN_TR = RIGHT CLICK

            if current_event['BTN_TL'] == 1:
                pass
                # return 'mouse_center'
            
            if current_event['BTN_TR'] == 1:
                # pydirectinput.click(button='right', _pause=False, duration=.3)
                # use mouseDown and mouseUp for right click
                pydirectinput.mouseDown(button='right')
                pydirectinput.mouseUp(button='right')
                # return 'mouse_right_click'
            
            # if current_event['BTN_TR'] == 0 and previous_event['BTN_TR'] == 1:
            #     # release right click when button is not pressed
            #     pydirectinput.mouseUp(button='right')
            #     return 'mouse_right_click_release'
            

            # X BUTTON: BTN_NORTH = w ability
            # B BUTTON: BTN_SOUTH = q ability
            # A BUTTON: BTN_EAST = e ability
            # Y BUTTON: BTN_WEST = r ultimate ability

            if current_event['BTN_NORTH'] == 1:
                button_press('w')
                # return 'w_ability'
            
            if current_event['BTN_SOUTH'] == 1:
                pydirectinput.press('q')
                # return 'q_ability'
            
            if current_event['BTN_EAST'] == 1:
                pydirectinput.press('e')
                # return 'e_ability'
            
            if current_event['BTN_WEST'] == 1:
                pydirectinput.press('r')
                # return 'r_ultimate_ability'
            

            # GAS TRIGGER: ABS_RZ = ENLARGE CIRCLE RADIUS
            # BREAK TRIGGER: ABS_Z = REDUCE CIRCLE RADIUS
            if current_event['ABS_RZ'] != 0:
                inc_val = current_event['ABS_RZ'] // 5  # Scale to a reasonable increment
                # grow_radius(inc_val)
                pass
                # return 'enlarge_circle_radius'
            if current_event['ABS_Z'] != 0:
                dec_value = current_event['ABS_Z'] // 5  # Scale to a reasonable decrement
                # shrink_radius(dec_value)
                pass
                # return 'reduce_circle_radius'


            # OPTION BUTTON: BTN_SELECT = HORN/PING BUTTON
            # SHARE BUTTON: BTN_START = ALL CHAT FLAME MACRO 3x
            if current_event['BTN_SELECT'] == 1:
                # play the horn sound
                # play_horn_sound()
                pydirectinput.press('u') # ping omw button

                
                # return 'ping_horn'
            if current_event['BTN_START'] == 1:
                # return 'all_chat_flame_macro'
                print("All chat flame macro triggered")
                # flame_macro()




if __name__ == "__main__":
    main()