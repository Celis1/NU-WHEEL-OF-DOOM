# from inputs import get_gamepad
import pyautogui
import pydirectinput
# import time
import math
import sounddevice as sd
import soundfile as sf
import threading
import time



import math
import time
import pyautogui

class OneEuro:
    """Tiny One-Euro filter for scalars (here: angle)."""
    def __init__(self, min_cutoff=1.5, beta=0.3, d_cutoff=1.0):
        self.min_cutoff = float(min_cutoff)
        self.beta = float(beta)
        self.d_cutoff = float(d_cutoff)
        self.x_prev = None
        self.dx_prev = None
        self.t_prev = None

    @staticmethod
    def _alpha(cutoff, dt):
        # cutoff in Hz → tau → alpha
        tau = 1.0 / (2.0 * math.pi * cutoff)
        return 1.0 / (1.0 + tau / dt)

    def __call__(self, t, x):
        if self.x_prev is None:
            self.x_prev, self.dx_prev, self.t_prev = x, 0.0, t
            return x

        dt = max(t - self.t_prev, 1e-3)
        # derivative smoothing
        dx = (x - self.x_prev) / dt
        a_d = self._alpha(self.d_cutoff, dt)
        dx_hat = a_d * dx + (1.0 - a_d) * self.dx_prev

        # main smoothing with adaptive cutoff
        cutoff = self.min_cutoff + self.beta * abs(dx_hat)
        a = self._alpha(cutoff, dt)
        x_hat = a * x + (1.0 - a) * self.x_prev

        self.x_prev, self.dx_prev, self.t_prev = x_hat, dx_hat, t
        return x_hat


class SmoothMouseController:
    def __init__(self,
                 center_x=None, center_y=None, radius=None,
                 dead_zone=100,         # larger than noise but < practical small movement
                 max_angle_degrees=270,  # total sweep from stick extremes
                 curve=1,             # >1 flattens near center to reduce jitter
                 min_cutoff=2, beta=0.35, d_cutoff=1.0,  # One-Euro params
                 pixel_threshold=1):      # hysteresis in screen space
        # Cache screen
        sw, sh = pyautogui.size()
        self.max_screen_width, self.max_screen_height = sw, sh

        # Mapping + shaping
        self.dead_zone = int(dead_zone)
        self.max_angle = math.radians(max_angle_degrees)
        self.curve = float(curve)

        # Filters
        self.angle_filter = OneEuro(min_cutoff=min_cutoff, beta=beta, d_cutoff=d_cutoff)

        # State
        self.default_angle = math.pi / 2  # straight up
        self.current_angle = self.default_angle
        self.last_norm = 0.0
        self.pixel_threshold_sq = float(pixel_threshold * pixel_threshold)
        self.last_x = None
        self.last_y = None

        # Raw stick bounds (signed 16-bit typical)
        self._RAW_MAX = 32767.0
        self._RAW_MIN = -32768.0
        self._DZ = float(self.dead_zone)


    def _normalize(self, raw):
        # flip axis if needed (match your original)
        raw = -float(raw)

        if -self.dead_zone <= raw <= self.dead_zone:
            return 0.0

        if raw > 0:
            norm = (raw - self._DZ) / (self._RAW_MAX - self._DZ)
        else:
            # FIX: correctly map negative side to [-1, 0]
            norm = (raw + self._DZ) / (-self._RAW_MIN - self._DZ)

        # clamp and shape
        norm = max(-1.0, min(1.0, norm))
        shaped = math.copysign(abs(norm) ** self.curve, norm)
        return shaped

    def abs_x_to_relative_radians(self, abs_x_value):
        """
        Convert ABS_X -> relative radians in [-max_angle, +max_angle] with shaping.
        No 'sticky' threshold here; the filter handles jitter adaptively.
        """
        norm = self._normalize(abs_x_value)
        self.last_norm = norm
        return norm * self.max_angle

    def radians_to_mouse_position(self,
                                  relative_radians, center_x, center_y, radius,
                                  starting_angle_radians=None,
                                  t=None):
        """
        Smooth the angle in time, then project to circle and apply small
        pixel hysteresis to avoid micro-updates. Returns (x, y).
        """
        if t is None:
            t = time.perf_counter()

        # Desired angle = base + relative
        base = self.default_angle if starting_angle_radians is None else float(starting_angle_radians)
        target_angle = base + float(relative_radians)

        # One-Euro filter (time-based, adaptive)
        filtered_angle = self.angle_filter(t, target_angle)
        self.current_angle = filtered_angle

        # Project to circle
        cx, cy, r = center_x, center_y, radius
        nx = cx + r * math.cos(filtered_angle)
        ny = cy - r * math.sin(filtered_angle)  # screen Y grows down

        # Hysteresis to kill tiny pixel-level jitter
        if self.last_x is not None:
            dx = nx - self.last_x
            dy = ny - self.last_y
            if (dx*dx + dy*dy) < self.pixel_threshold_sq:
                nx, ny = self.last_x, self.last_y
        self.last_x, self.last_y = nx, ny

        # Clamp & return ints
        final_x = max(0, min(self.max_screen_width  - 1, int(nx)))
        final_y = max(0, min(self.max_screen_height - 1, int(ny)))
        return final_x, final_y


class GameScreenMouse(SmoothMouseController):
    def __init__(self):
        super().__init__()
        # mouse starting position distance from center
        self.character_radius = 40  # character radius in pixels
        self.attack_rang = 200  # attack range in pixels
        self.walk_range = 500  # walk range in pixels

        self.original_radius = self.attack_rang
        self.current_radius = self.original_radius 
        
        self.disbale_mouse = False

        self.curr_radian_val = 0.0

        # offsets per side
        self.offset_x = -80
        self.offset_y = -20
        self.curr_side = 'blue'
        self.offset_blue = [-80, -20]
        self.offset_red = [70, -170]

        # champion center position
        print(f' Screen size: {self.max_screen_width}x{self.max_screen_height}')
        self.center_x = (self.max_screen_width // 2) + self.offset_x
        self.center_y = (self.max_screen_height // 2) + self.offset_y
        print(f' Center position: {self.center_x}, {self.center_y}')

    def _center_mouse(self):
        ''' ONLY FOR TESTING PURPOSES '''
        self.move_mouse(self.center_x, self.center_y)


    def quarter_step_mouse(self, cardinal_direction='N'):
        """Move the mouse in a quarter step based on cardinal direction."""
        if cardinal_direction == 'N':
            self.default_angle = math.pi / 2
        elif cardinal_direction == 'E':
            self.default_angle = 0
        elif cardinal_direction == 'S':
            self.default_angle = -math.pi / 2
        elif cardinal_direction == 'W':
            self.default_angle = math.pi

    def swap_mouse_lock(self):
        self.disbale_mouse = not self.disbale_mouse

    def rotate_mouse(self, abs_x_value, starting_angle_radians=None):

        # check if mouse is disabled
        if self.disbale_mouse:
            return       

        radian_val = self.abs_x_to_relative_radians(int(abs_x_value))
        
        X_POS, Y_POS = self.radians_to_mouse_position(radian_val,
                                                    self.center_x,
                                                    self.center_y,
                                                    self.current_radius,
                                                    starting_angle_radians)

        if X_POS >= self.max_screen_width:
            X_POS = self.max_screen_width - 100
        elif X_POS <= 0:
            X_POS = 10

        if Y_POS >= self.max_screen_height:
            Y_POS = self.max_screen_height - 100
        elif Y_POS <= 0:
            Y_POS = 10

        self.move_mouse(X_POS, Y_POS)


    def modify_radius(self, input_val):

        # changing the radius
        modify_val = input_val

        if modify_val < 0:
            self.current_radius = self.original_radius + modify_val/2
        else:
            self.current_radius = self.original_radius + modify_val


        if self.current_radius < self.character_radius:
            self.current_radius = self.character_radius



    def set_radius(self, radius_size):
        '''
        radius_size: string  
            'small' - charcater radius
            'medium' - combat radius
            'large' - clicking radius
            'verylarge' - drifting radius
        '''
        if radius_size == 'small':
            self.current_radius = self.character_radius

        elif radius_size == 'medium':
            self.current_radius = self.attack_rang
        
        elif radius_size == 'large':
            self.current_radius = self.walk_range

        
      
    def shop_offset(self, value):

        if value == 0:
            # self.offset_x, self.offset_y = 0, 0
            if self.curr_side == 'blue':
                self.offset_x, self.offset_y = self.offset_blue
            elif self.curr_side == 'red':
                self.offset_x, self.offset_y = self.offset_red

        else: 
            self.offset_x = -80
            self.offset_y = 100

        self.center_x = (self.max_screen_width // 2) + self.offset_x
        self.center_y = (self.max_screen_height // 2) + self.offset_y
            
        
    def swap_offset_side(self):
        if self.curr_side == 'blue':
            self.offset_x, self.offset_y = self.offset_red
            self.curr_side = 'red'
        else:
            self.offset_x, self.offset_y = self.offset_blue
            self.curr_side = 'blue'

        self.center_x = (self.max_screen_width // 2) + self.offset_x
        self.center_y = (self.max_screen_height // 2) + self.offset_y
        

    def move_mouse(self, x, y):
        def move_mouse_thread():
            """Move the mouse to the specified coordinates."""
            pyautogui.moveTo(x, y)
        
        """Simulate mouse movement."""
        threading.Thread(target=move_mouse_thread).start()
    
    def click_mouse(self, button='right', shift=False):
        def click_func():
            """Click the mouse button."""
            if button == 'right':
                pydirectinput.mouseDown(button='right')
                pydirectinput.mouseUp(button='right')
            elif button == 'left':
                pydirectinput.mouseDown(button='left')
                pydirectinput.mouseUp(button='left')

        def shift_click_func():
            pydirectinput.keyDown('shift')
            pydirectinput.mouseDown(button='right')
            pydirectinput.keyUp('shift')
            pydirectinput.mouseUp(button='right')
  
        if shift:
            threading.Thread(target=shift_click_func).start()
        else:
            threading.Thread(target=click_func).start()

   
if __name__ == "__main__":

    from controller_read import Controller

    controller = Controller()
    mouse = GameScreenMouse()

    while True:
        # Read controller input
        controller.read()

        # Rotate mouse based on ABS_X input
        mouse.rotate_mouse(controller.buttons['ABS_X'])

        # Update radius based on ABS_Y input
        controller.update_pedals()
