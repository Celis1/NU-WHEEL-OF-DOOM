import time
import sounddevice as sd
import soundfile as sf
import threading


from controller_read import Controller

class WheelOfDoom(Controller):
    def __init__(self):
        self.controller = Controller()
        self.controller_thread = self.init_controller()
        self.controller_disable = False

    def read_controller_thread(self, controller):
        while not self.controller_disable:
            controller.read()

    def init_controller(self):
        temp = threading.Thread(target=self.read_controller_thread, args=(self.controller,))
        temp.daemon = True  # This line makes it exit when main program exits
        return temp
    
    def run(self):
        print("Starting Wheel of Doom controller...")

        try:
            self.controller_thread.start()

            while not self.controller_disable:
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