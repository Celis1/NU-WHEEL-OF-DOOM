# Core Button Mapping

## Abilities we need
    - right click
    - left click (optional)
    - shift + right click attack champion move (optional)

    - q ability 
    - w abiltiy
    - e ability 
    - r ability
    - d ability flash
    - f ability smite

    - ctrl q lvl ability 
    - ctrl w lvl abiltiy
    - ctrl e lvl ability 
    - ctrl r lvl ability

    - 1 item slot (optional)
    - 2 item slot
    - 3 item slot
    - 4 ward item slot

    - s stop moving
    - ` attack champion only

    - u ping on my way
    - k retreat ping (optional)

    - b recall
    - tab leaderboard
    - p shop


    - f1 view ally 1
    - f2 view ally 2 
    - f3 view ally 3 
    - f4 view ally 4


    (OPTIONALS)
    - ctrl + 4 laugh emote
    - ctrl + 6 mastery flex
    - t thumbs up emote

## Translation
    'BTN_TL': 'PADDLE L',
    'BTN_TR': 'PADDLE R',
    'BTN_THUMBL': 'BACK L',
    'BTN_THUMBR': 'BACK R',

    'BTN_WEST': 'Y BUTTON',
    'BTN_NORTH': 'X BUTTON',
    'BTN_EAST': 'A BUTTON',
    'BTN_SOUTH': 'B BUTTON',

    'BTN_SELECT': 'OPTION BUTTON',
    'BTN_START': 'SHARE BUTTON',

    'ABS_HAT0X': 'DPAD_LEFT_RIGHT', # -1, 0, 1
    'ABS_HAT0Y': 'DPAD_UP_DOWN',    # -1, 0, 1

    
    'ABS_Z': 'PEDAL_GAS',  # 0 to 255
    'ABS_RZ': 'PEDAL_BRAKE', # 0 to 255
    'ABS_X': 'WHEEL', # -32768 to 32767
        

## - Button mappings to my steering wheel 
    - (1) PADDLE R = right click -1- -0-
    - (2) PADDLE L + BACK L = left click -2- -0-
    - (3) PADDLE L + Paddle R = ` attack move -2- -0-

    - (4) B BUTTON: BTN_WEST = q ability -1-
    - (5) X BUTTON: BTN_NORTH = w ability -1-
    - (6) A BUTTON: BTN_EAST = e ability -1-
    - (7) Y BUTTON: BTN_SOUTH = r ultimate ability -1-
    - (8) PADDLE L + X BUTTON = d flash ability -2- -0-
    - (9) PADDLE L + A BUTTON = f smite ability -2- -0-

    - (10) BACK L + B BUTTON: BTN_SOUTH = lvl q ability -2- -0-
    - (11) BACK L + X BUTTON: BTN_NORTH = lvl w ability -2- -0-
    - (12) BACK L + A BUTTON: BTN_EAST = lvl e ability -2- -0-
    - (13) BACK L + Y BUTTON: BTN_WEST = lvl r ability -2- -0-

    - (14) PADDLE L + D-PAD RIGHT: ABS_HAT0X 1 = item 2 -2-
    - (15) BACK R + D-PAD DOWN: ABS_HAT0Y 1 = item 3 -2-
    - (16) BACK R + D-PAD LEFT: ABS_HAT0X -1 = item 4 ward -2-
    - (17) BACK R + D-PAD UP: ABS_HAT0Y -1 = s stop moving -2-
    
    - (18) BACK L + D-PAD RIGHT: ABS_HAT0X 1 = ` attack champion only -!-(REMOVE THIS ITS OUR PADDLE L + PADDLE R) -2-

    - (19) OPTION BUTTON: BTN_SELECT = u ping on my way + horn -1-
    - (20) PADDLE L + D-PAD(ANY DIRECTION) + OPTION BUTTON: BTN_SELECT = ping retreat -3-

    - (21) BACK L + D-PAD UP: ABS_HAT0Y -1 = tab leaderboard -2-
    - (22) BACK L + D-PAD LEFT: ABS_HAT0X -1 = p shop -2-
    - (23) BACK L + D-PAD DOWN: ABS_HAT0Y 1 = b recall -2-


    
    [REVISE THIS WE WANT COMBO DPAD BUTTON TO FREE UP PADDLE L WITH DPAD]
    - (24) PADDLE L + D-PAD UP: ABS_HAT0Y -1 = f2 view ally 1 -2-
    - (25) PADDLE L + D-PAD RIGHT: ABS_HAT0X 1 = f3 view ally 2 -2-
    - (26) PADDLE L + D-PAD DOWN: ABS_HAT0Y 1 = f4 view ally 3 -2-
    - (27) PADDLE L + D-PAD LEFT: ABS_HAT0X -1 = f5 view ally 4 -2-


    (OPTIONALS)

    - (28) BACK L + BACK R +  D-PAD RIGHT: ABS_HAT0X 1 = laugh emote -3-
    - (29) BACK L + BACK R + D-PAD UP: ABS_HAT0Y -1 = t thumbs up emote -3-

## CORE MOUSE MOVEMENTS
    - (30) PEDAL BREAK : ABS_Z = SHRINK RADIUS -1-
    - (31) PEDAL GAS : ABS_RZ = ENLARGE RADIUS -1-

    [CHANGE THIS TO BE MAX RADIUS ON MAX VALUE]
    - (32) BACK L + BACK R + PEDAL GAS : ABS_RZ = MAX RADIUS -3-
    - (33) BACK L + BACK R + PEDAL BREAK : ABS_Z = MIN RADIUS -3-


    - (34) PADDLE L + OPTION BUTTON: BTN_SELECT + SHARE BUTTON: BTN_START = space LOCK CAMERA -3-
    - (35) BACK L + OPTION BUTTON: BTN_SELECT + SHARE BUTTON: BTN_START = CHANGE SIDE OFFSET -3-


    - (36) D-PAD = pi radian depending on dpad direction -1-

    <!-- - (37) PADDLE L + BACK R + D-PAD = absolute mouse movement -->
    <!-- - (38) PADDLE L + B BUTTON: BTN_SOUTH + D-PAD(ANY DIRECTION) = click and drag -->



--- NOTE 
PADDLE L + WEST BUTTON
BACK R + ANY CORE BUTTONS
SHARE BUTTON + ANYTHING 