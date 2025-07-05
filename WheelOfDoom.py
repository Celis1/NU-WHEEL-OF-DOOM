# from inputs import get_gamepad
# import pyautogui
# import pydirectinput
import time
# import math
import sounddevice as sd
import soundfile as sf
import threading

from my_controller import Controller

class WheelOfDoom(Controller):
    pass

# TODO: controller doesnt update if there no change in input

def read_controller_thread(controller):

    while True:
        controller.read()



if __name__ == "__main__":
    fps = 60
    frame_time = 1.0 / fps  # ~0.0167 seconds per frame
    last_frame_time = time.time()

    controller = Controller()

    # thread this function
    # values = controller.read()
    # print(values)

    temp = threading.Thread(target=read_controller_thread, args=(controller,))
    temp.start()

    print("Starting Wheel of Doom controller...")
    while True:
        current_time = time.time()

        # cap the frame rate
        if current_time - last_frame_time >= frame_time:
            controller.rotate_mouse(controller.current_event['ABS_X'])
            controller.get_action()
            print(controller.current_event)

            last_frame_time = current_time
