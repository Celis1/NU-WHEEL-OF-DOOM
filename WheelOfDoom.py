# from inputs import get_gamepad
# import pyautogui
# import pydirectinput
# import time
# import math
import sounddevice as sd
import soundfile as sf
# import threading

from my_controller import Controller

class WheelOfDoom(Controller):
    pass


if __name__ == "__main__":
    controller = Controller()

    print("Starting Wheel of Doom controller...")
    while True:
        values = controller.read()
        print(values)

        controller.rotate_mouse(values['ABS_X'])

        controller.get_action()
