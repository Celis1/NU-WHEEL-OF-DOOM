
basic_ev_types = {'Absolute', 'Key', 'Sync'}
abs_set = {'ABS_X', 'ABS_HAT0Y', 'ABS_RY', 'ABS_Z', 'ABS_HAT0X', 'ABS_RZ'}
key_set = {'BTN_TR', 'BTN_SOUTH', 'BTN_START', 'BTN_SELECT', 'BTN_NORTH', 'BTN_WEST', 'BTN_TL', 'BTN_EAST'}
sync_set = {'SYN_REPORT'}

abs_dict = {'ABS_X': [-32768, 'RANGE', 32767], 'ABS_RZ': [0, 'RANGE', 255], 'ABS_Z': [0, 'RANGE', 255], 'ABS_HAT0Y': {0, 1, -1}, 'ABS_HAT0X': {0, 1, -1}, 'ABS_RY': {0,-1}}

key_dict = {'BTN_TL': {0, 1}, 'BTN_TR': {0, 1}, 'BTN_WEST': {0, 1}, 'BTN_NORTH': {0, 1}, 'BTN_EAST': {0, 1}, 'BTN_SOUTH': {0, 1}, 'BTN_START': {0, 1}, 'BTN_SELECT': {0, 1}, 'BTN_THUMBR': {0, 1}, 'BTN_THUMBL': {0, 1}}