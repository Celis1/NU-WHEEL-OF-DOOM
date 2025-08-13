#!/usr/bin/env python3
"""
Controller script for managing the Wheel of Doom process.
This allows you to start, stop, and monitor the wheel process at will.
"""

import subprocess
import time
import signal
import os
import sys
from pathlib import Path

class WheelProcessManager:
    def __init__(self, script_path="WheelOfDoom.py"):
        """
        Initialize the process manager.
        
        Args:
            script_path (str): Path to your WheelOfDoom.py script
        """
        self.script_path = script_path
        self.process = None
        self.is_running = False
        
        # Verify the script exists
        if not Path(script_path).exists():
            print(f"Error: Script '{script_path}' not found!")
            return
    
    def start_wheel(self):
        """Start the Wheel of Doom process"""
        if self.is_running:
            print("Wheel of Doom is already running!")
            return False
        
        try:
            print("Starting Wheel of Doom process...")
            # Start the process
            self.process = subprocess.Popen([
                sys.executable, self.script_path
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Give it a moment to start
            time.sleep(0.5)
            
            # Check if it's still running (didn't crash immediately)
            if self.process.poll() is None:
                self.is_running = True
                print(f"✓ Wheel of Doom started successfully! PID: {self.process.pid}")
                return True
            else:
                # Process died immediately, show error
                stdout, stderr = self.process.communicate()
                print("✗ Wheel of Doom failed to start!")
                if stderr:
                    print(f"Error: {stderr}")
                return False
                
        except Exception as e:
            print(f"✗ Failed to start Wheel of Doom: {e}")
            return False
    
    def stop_wheel(self):
        """Stop the Wheel of Doom process"""
        if not self.is_running or self.process is None:
            print("Wheel of Doom is not running.")
            return True
        
        try:
            print("Stopping Wheel of Doom process...")
            
            # First try graceful termination (SIGTERM)
            self.process.terminate()
            
            # Wait up to 5 seconds for graceful shutdown
            try:
                self.process.wait(timeout=5)
                print("✓ Wheel of Doom stopped gracefully.")
            except subprocess.TimeoutExpired:
                # If it doesn't respond, force kill it
                print("Process didn't respond to termination, force killing...")
                self.process.kill()
                self.process.wait()
                print("✓ Wheel of Doom force stopped.")
            
            self.is_running = False
            self.process = None
            return True
            
        except Exception as e:
            print(f"✗ Error stopping Wheel of Doom: {e}")
            return False
    
    def restart_wheel(self):
        """Restart the Wheel of Doom process"""
        print("Restarting Wheel of Doom...")
        if self.is_running:
            self.stop_wheel()
            time.sleep(1)  # Brief pause between stop and start
        return self.start_wheel()
    
    def get_status(self):
        """Get the current status of the process"""
        if not self.is_running or self.process is None:
            return "Not running"
        
        # Check if process is still alive
        poll_result = self.process.poll()
        if poll_result is None:
            return f"Running (PID: {self.process.pid})"
        else:
            # Process died
            self.is_running = False
            return f"Stopped (exit code: {poll_result})"
    
    def monitor(self, check_interval=2):
        """
        Monitor the process and show its status continuously.
        Press Ctrl+C to stop monitoring.
        """
        print("Monitoring Wheel of Doom process... (Ctrl+C to stop monitoring)")
        try:
            while True:
                status = self.get_status()
                print(f"Status: {status}")
                
                # If process died unexpectedly, break the loop
                if self.is_running and self.process and self.process.poll() is not None:
                    print("Process terminated unexpectedly!")
                    self.is_running = False
                    break
                
                time.sleep(check_interval)
        except KeyboardInterrupt:
            print("\nStopped monitoring.")

def main():
    """Main function - simplified for GUI integration"""
    # Create the process manager with default script path
    manager = WheelProcessManager("WheelOfDoom.py")
    return manager

if __name__ == "__main__":
    # For testing - create manager and show basic info
    manager = main()
    print("Wheel Process Manager initialized")
    print("Use manager.start_wheel() and manager.stop_wheel() to control the process")