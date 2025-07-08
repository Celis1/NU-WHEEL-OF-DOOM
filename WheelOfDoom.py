import time
import sounddevice as sd
import soundfile as sf
import threading

# # from my_controller import Controller
# from advanced_controller import Controller as AdvancedController

print('before input')
from controller_read import Controller


class WheelOfDoom(Controller):
    pass

def read_controller_thread(controller):
    while True:
        controller.read()

def read_contious_vals(controller):
    # fps = 600 # keep at 120
    # frame_time = 1.0 / fps  
    # last_frame_time = time.time()

    while True:
        current_time = time.time()  # You're missing this line!
        
        # cap the frame rate
        # if current_time - last_frame_time >= frame_time:
        controller.rotate_mouse(controller.buttons['ABS_X'])
        controller.update_pedals()
            
            # last_frame_time = current_time  # Only update AFTER frame executes


if __name__ == "__main__":
    # fps = 120 # keep at 120
    # frame_time = 1.0 / fps  
    # last_frame_time = time.time()


    print("Initializing Wheel of Doom controller...")
    controller = Controller()

    # Make it a daemon thread - it will die when main program exits
    temp = threading.Thread(target=read_contious_vals, args=(controller,))
    temp.daemon = True  # This line makes it exit when main program exits
    temp.start()


    print("Starting Wheel of Doom controller...")
    try:
        while True:
            current_time = time.time()

            # get controller input
            controller.read()

            print()
            action_went_though = controller.call_action()
            # print(controller.current_event)
            print(controller.get_pressed_buttons_info())
            

            last_frame_time = current_time

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Exiting Wheel of Doom controller...")

    except KeyboardInterrupt:
        print("\nShutting down...")