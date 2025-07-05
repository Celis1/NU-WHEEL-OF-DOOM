from inputs import get_gamepad
import math
import threading
import time

basic_ev_types = {'Absolute', 'Key', 'Sync'}

abs_set = {'ABS_X', 'ABS_HAT0Y', 'ABS_RY', 'ABS_Z', 'ABS_HAT0X', 'ABS_RZ'}
key_set = {'BTN_TR', 'BTN_SOUTH', 'BTN_START', 'BTN_SELECT', 'BTN_NORTH', 'BTN_WEST', 'BTN_TL', 'BTN_EAST'}
sync_set = {'SYN_REPORT'}

abs_dict = {}
key_dict = {'BTN_TL': {0, 1}, 'BTN_TR': {0, 1}, 'BTN_WEST': {0, 1}, 'BTN_NORTH': {0, 1}, 'BTN_EAST': {0, 1}, 'BTN_SOUTH': {0, 1}, 'BTN_START': {0, 1}, 'BTN_SELECT': {0, 1}}

def main():
    """Just print out some event infomation when the gamepad is used."""
    try:
        while 1:
            events = get_gamepad()
            for event in events:
                print(event.ev_type, event.code, event.state)
                #checking unique event types
                if event.ev_type == 'Absolute':
                    if event.code not in abs_dict:
                        abs_dict[event.code] = set()
                    elif event.code in abs_dict:
                        abs_dict[event.code].add(event.state)


                elif event.ev_type == 'Key':
                    if event.code not in key_dict:
                        key_dict[event.code] = set()
                    elif event.code in key_dict:
                        key_dict[event.code].add(event.state)

                # elif event.ev_type == 'Sync':
                #     sync_set.add(event.code)

    except KeyboardInterrupt:
        print("Exiting...")
        # print("Absolute events:", len(abs_set), "Unique codes:", abs_set)
        # print("Key events:", len(key_set), "Unique codes:", key_set)
        # print("Sync events:", len(sync_set), "Unique codes:", sync_set)

        for i in abs_dict:
            if len(abs_dict[i]) > 10:
                temp_min = min(abs_dict[i])
                temp_max = max(abs_dict[i])
                abs_dict[i] = [temp_min, 'RANGE', temp_max]

        print("Absolute events:", len(abs_dict), "Unique codes:", abs_dict)
        print("Key events:", len(key_dict), "Unique codes:", key_dict)

if __name__ == "__main__":
    main()