import tkinter as tk
from tkinter import messagebox
import requests
from PIL import Image, ImageTk
import io
from itertools import cycle
import threading
import time

# my imports
from WheelProcess import WheelProcessManager
# from WheelOfDoom import WheelOfDoom

class WheelOfDoomApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NU Wheel of Doom")
        # Updated dimensions to 1920x1080 (landscape)
        self.window_width = 1920
        self.window_height = 1080
        
        self.root.geometry(f"{self.window_width}x{self.window_height}")
        self.root.resizable(False, False)
        
        # Dark mode colors
        self.bg_color = '#1e1e1e'
        self.fg_color = '#ffffff'
        self.button_bg = '#333333'
        self.button_fg = '#ffffff'
        
        self.root.configure(bg=self.bg_color)
        
        # Center the window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.window_width // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.window_height // 2)
        self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")
        
        # GIF URLs
        self.controller_disabled_gif_url = "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExbjZiZWs5ZnV3ajA5OHVoa2xtYjA4NTMzYjJ3ZDl3ZWxhMjI0d3oxdyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/mdWoqhOwsxwlqWKSUQ/giphy.gif"
        self.default_gif_url = "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExZGMzejR2MjN1bzI2Ymhld3FuMmZvNzBmeGN3YjluZmNodDh5aWhodSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/tY0Li19HJ2unvdoLoy/giphy.gif"
        
        # State tracking - Both start as disabled (True means disabled)
        self.controller_disabled_state = True
        self.horn_disabled_state = True
        self.current_frames = []
        self.frame_cycle = None
        self.animation_running = False
        self.controller_thread = None  # Initialize thread variable
        self.wheel_of_doom = None  # Initialize wheel instance
        self.controller_process = None  # Initialize process variable
        
        self.setup_ui()
        self.load_hardcoded_images()
        # Load controller disabled GIF since controller starts disabled
        self.load_controller_disabled_gif()

        # Loading my Wheel of Doom controller
        # Initialize but don't start the wheel
        self.wheel_manager = WheelProcessManager("./WheelOfDoom.py")

        
        # # Set up window closing protocol
        # self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_ui(self):
        # Main container - use fixed heights to ensure everything fits
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)
        
        # Top section container - fixed height
        top_section = tk.Frame(main_frame, bg=self.bg_color, height=250)
        top_section.pack(fill=tk.X, pady=10)
        top_section.pack_propagate(False)  # Prevent resizing
        
        # Stream image section
        self.stream_image_label = tk.Label(
            top_section,
            bg=self.bg_color,
            text="Stream Image Here",
            font=("Arial", 20),
            fg=self.fg_color
        )
        self.stream_image_label.pack(pady=10)
        
        # Title
        title_label = tk.Label(
            top_section, 
            text="NU Wheel of Doom", 
            font=("Arial", 36, "bold"),
            bg=self.bg_color,
            fg=self.fg_color
        )
        title_label.pack(pady=10)
        
        # GIF container with calculated height to fit everything
        # Total height: 1080 - 40 (pady) - 250 (top) - 100 (buttons) - 60 (spacing) = 630
        gif_container = tk.Frame(main_frame, bg=self.bg_color, height=630)
        gif_container.pack(fill=tk.X, pady=10)
        gif_container.pack_propagate(False)  # Prevent frame from resizing
        
        self.gif_label = tk.Label(gif_container, bg=self.bg_color, cursor="hand2")
        self.gif_label.pack(expand=True)
        
        # Make GIF clickable - bind click event to controller_disabled function
        self.gif_label.bind("<Button-1>", lambda event: self.controller_disabled())
        
        # Button frame - fixed height at bottom
        button_frame = tk.Frame(main_frame, bg=self.bg_color, height=100)
        button_frame.pack(fill=tk.X, pady=20)
        button_frame.pack_propagate(False)  # Prevent resizing
        
        # Create a centered container for buttons
        button_container = tk.Frame(button_frame, bg=self.bg_color)
        button_container.pack(expand=True)
        
        # Horn disabled button
        self.horn_btn = tk.Button(
            button_container,
            text="Horn Disabled",
            command=self.horn_disabled,
            bg='#ff4444',  # Start red (disabled)
            fg=self.button_fg,
            font=('Arial', 16, 'bold'),
            relief='flat',
            padx=40,
            pady=12,
            activebackground='#555555',
            activeforeground=self.button_fg,
            width=18
        )
        self.horn_btn.pack(side=tk.LEFT, padx=30)
        
        # Controller disabled button
        self.controller_btn = tk.Button(
            button_container,
            text="Controller Disabled",
            command=self.controller_disabled,
            bg='#ff4444',  # Start red (disabled)
            fg=self.button_fg,
            font=('Arial', 16, 'bold'),
            relief='flat',
            padx=40,
            pady=12,
            activebackground='#555555',
            activeforeground=self.button_fg,
            width=18
        )
        self.controller_btn.pack(side=tk.LEFT, padx=30)

        
    def load_hardcoded_images(self):
        """Load hardcoded images"""
        # TODO: Replace with your actual image paths
        stream_image_path = "F:\\ChallengerYCY\\Brand\Banner\CHALLENGERYCY-cropped.png"
        icon_path = "F:\\ChallengerYCY\\Brand\RAW\just_head-Photoroom.png"
        
        # TODO: Uncomment and modify these lines to load your images
        self.load_stream_image_from_path(stream_image_path)
        self.load_icon_from_path(icon_path)
        
        pass
    
    def load_stream_image_from_path(self, image_path):
        """Load stream image from hardcoded path"""
        try:
            # Load and process the image
            image = Image.open(image_path)
            
            # Calculate dimensions to fit in the top section (scaled up for 1920x1080)
            target_height = 150  # Increased from 80
            target_width = int(target_height * (image.width / image.height))
            
            # If too wide, limit width instead (scaled up)
            if target_width > 1000:  # Increased from 500
                target_width = 1000
                target_height = int(target_width * (image.height / image.width))
            
            # Resize the image
            resized_image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(resized_image)
            
            # Update the label
            self.stream_image_label.configure(image=photo, text="")
            self.stream_image_label.image = photo  # Keep a reference
            
        except Exception as e:
            print(f"Failed to load stream image: {e}")
    
    def load_icon_from_path(self, icon_path):
        """Load application icon from hardcoded path"""
        try:
            if icon_path.lower().endswith('.ico'):
                # For ICO files, use directly
                self.root.iconbitmap(icon_path)
            else:
                # For PNG files, convert to PhotoImage
                icon_image = Image.open(icon_path)
                # Resize to appropriate icon size
                icon_image = icon_image.resize((64, 64), Image.Resampling.LANCZOS)
                icon_photo = ImageTk.PhotoImage(icon_image)
                self.root.iconphoto(True, icon_photo)
                # Keep reference to prevent garbage collection
                self.icon_photo = icon_photo
                
        except Exception as e:
            print(f"Failed to load icon: {e}")
    
    def load_gif_from_url(self, url):
        """Load GIF from URL and return frames"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            gif_data = io.BytesIO(response.content)
            gif_image = Image.open(gif_data)
            
            frames = []
            try:
                while True:
                    frame = gif_image.copy()
                    # Size GIF to fit in the 630px height container
                    frame = frame.resize((600, 600), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(frame)
                    frames.append(photo)
                    gif_image.seek(len(frames))
            except EOFError:
                pass
            
            return frames
            
        except Exception as e:
            print(f"Error loading GIF from {url}: {e}")
            return []
    
    def load_default_gif(self):
        """Load the default spinning wheel GIF"""
        self.current_frames = self.load_gif_from_url(self.default_gif_url)
        if self.current_frames:
            self.frame_cycle = cycle(self.current_frames)
            self.start_animation()
        else:
            self.show_gif_error()
    
    def load_controller_disabled_gif(self):
        """Load the controller disabled GIF"""
        frames = self.load_gif_from_url(self.controller_disabled_gif_url)
        if frames:
            self.current_frames = frames
            self.frame_cycle = cycle(self.current_frames)
            if not self.animation_running:
                self.start_animation()
        else:
            self.show_gif_error()
    
    def start_animation(self):
        """Start the GIF animation"""
        if not self.animation_running:
            self.animation_running = True
            self.animate_gif()
    
    def animate_gif(self):
        """Animate the current GIF"""
        if self.animation_running and hasattr(self, 'frame_cycle') and self.frame_cycle:
            try:
                frame = next(self.frame_cycle)
                self.gif_label.configure(image=frame)
                self.root.after(100, self.animate_gif)
            except:
                self.animation_running = False
    
    def show_gif_error(self):
        """Show error message when GIF fails to load"""
        error_label = tk.Label(
            self.gif_label,
            text="Failed to load GIF",
            font=("Arial", 32),  # Increased font size
            bg=self.bg_color,
            fg='#888888'
        )
        error_label.pack(expand=True)
    
    def horn_disabled(self):
        """Handle horn disabled button click - toggleable"""
        
        self.horn_disabled_state = not self.horn_disabled_state
        
        if self.horn_disabled_state:
            print("horn disabled")
            self.horn_btn.configure(text="Horn Disabled", bg='#ff4444')
        else:
            print("horn enabled")
            self.horn_btn.configure(text="Horn Enabled", bg='#44ff44')  # Green for enabled

    def controller_disabled(self):
        """Handle controller disabled button click - toggleable"""
        print("controller button clicked")
        
        # Toggle controller disabled state
        self.controller_disabled_state = not self.controller_disabled_state
        
        if self.controller_disabled_state:
            # Stop the wheel process
            self.wheel_manager.stop_wheel()
            
            # Switch to controller disabled GIF
            self.load_controller_disabled_gif()
            self.controller_btn.configure(text="Controller Disabled", bg='#ff4444')
            
        else:
            # Start the wheel process
            self.wheel_manager.start_wheel()
            
            # Switch back to default GIF
            self.load_default_gif()
            self.controller_btn.configure(text="Controller Enabled", bg='#44ff44') 

    # def on_closing(self):
    #     """Handle window closing event - clean up processes"""
    #     print("Closing application...")
        
    #     # Stop the wheel process if it's running
    #     if hasattr(self, 'wheel_manager') and self.wheel_manager.is_running:
    #         print("Stopping wheel process...")
    #         self.wheel_manager.stop_wheel()
        
    #     # Destroy the window
    #     self.root.destroy()


def main():
    root = tk.Tk()
    app = WheelOfDoomApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()