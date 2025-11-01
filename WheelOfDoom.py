import sounddevice as sd
import soundfile as sf
import threading

from controller_read import Controller



import time

def rate_counter(name="rate", window=1.0):
    def deco(fn):
        count, start = 0, time.perf_counter()
        def wrapped(*a, **kw):
            nonlocal count, start
            count += 1
            now = time.perf_counter()
            if now - start >= window:
                print(f"{name}: {count/(now-start):.0f} calls/sec")
                count, start = 0, now
            return fn(*a, **kw)
        return wrapped
    return deco

class WheelOfDoom(Controller):
    def __init__(self):
        self.controller = Controller()
        self.controller_thread = self.init_controller()

    def read_controller_thread(self, controller):
        while True:
            controller.read()

    def init_controller(self):
        temp = threading.Thread(target=self.read_controller_thread, args=(self.controller,))
        # This line makes it exit when main program exits
        temp.daemon = True 
        return temp
    
    def run(self):
        print("Starting Wheel of Doom controller...")
        try:
            self.controller_thread.start()

            while True:
                self.controller.rotate_mouse(self.controller.buttons['ABS_X'])
                self.controller.update_pedals()
                action_went_though = self.controller.call_action()


        except Exception as e:
            print(f"An error occurred: {e}")
            print("Exiting Wheel of Doom controller...")

        except KeyboardInterrupt:
            print("\nShutting down...")



if __name__ == "__main__":

    THE_WHEEL = WheelOfDoom()
    THE_WHEEL.run()