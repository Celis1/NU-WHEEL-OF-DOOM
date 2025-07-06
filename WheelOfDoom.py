import time
import sounddevice as sd
import soundfile as sf
import threading

from my_controller import Controller



# TODO: WE WANT A MIDDLE RADIUS THAT WE CAN SWAP TO
# TODO: 

class WheelOfDoom(Controller):
    pass

def read_controller_thread(controller):
    while True:
        controller.read()

if __name__ == "__main__":
    fps = 10 # keep at 120
    frame_time = 1.0 / fps  
    last_frame_time = time.time()

    controller = Controller()

    # Make it a daemon thread - it will die when main program exits
    temp = threading.Thread(target=read_controller_thread, args=(controller,))
    temp.daemon = True  # This line makes it exit when main program exits
    temp.start()

    # TODO : only updates or changes to inputs should added to a queue to read
    # TODO : AND OUR READ FUNCTION WILL READ THE QUEUE INSTEAD OF THE DEVICE DIRECTLY

    print("Starting Wheel of Doom controller...")
    try:
        while True:
            current_time = time.time()

            # cap the frame rate
            if current_time - last_frame_time >= frame_time:
                controller.rotate_mouse(controller.current_event['ABS_X'])
                controller.get_action()
                print(controller.current_event)
              

                last_frame_time = current_time
    except KeyboardInterrupt:
        print("\nShutting down...")