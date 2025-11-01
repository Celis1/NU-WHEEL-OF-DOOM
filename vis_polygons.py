import sys
import tkinter as tk
import ctypes

# ---- Overlay that visualizes KeepOutZones on-screen ----
class ZoneOverlay:
    def __init__(self, zones,
                 line_width=2,
                 color_rect="#ff4444",
                 color_poly="#00ffff",
                 show_centroids=True,
                 click_through=True,
                 transparent_color="magenta",
                 refresh_ms=100):
        self.zones = zones
        self.line_width = int(line_width)
        self.color_rect = color_rect
        self.color_poly = color_poly
        self.show_centroids = show_centroids
        self.refresh_ms = int(refresh_ms)

        self.root = tk.Tk()
        self.root.overrideredirect(True)          # borderless
        self.root.attributes("-topmost", True)
        self.root.geometry(f"{zones.sw}x{zones.sh}+0+0")

        # Transparent background (Windows Tk 8.6+)
        self.canvas = tk.Canvas(self.root, width=zones.sw, height=zones.sh,
                                highlightthickness=0, bg=transparent_color)
        try:
            self.root.wm_attributes("-transparentcolor", transparent_color)
        except tk.TclError:
            # Fallback: semi-transparency (not click-through)
            self.root.attributes("-alpha", 0.5)

        self.canvas.pack(fill="both", expand=True)

        # Make overlay ignore mouse clicks (Windows only)
        if sys.platform.startswith("win") and click_through:
            self._make_click_through()

        # Hotkeys
        self.visible = True
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        self.root.bind("<F8>", self._toggle_visibility)

        # Start drawing
        self._tick()
        self.root.mainloop()

    def _make_click_through(self):
        # WS_EX_LAYERED | WS_EX_TRANSPARENT
        GWL_EXSTYLE = -20
        WS_EX_LAYERED = 0x00080000
        WS_EX_TRANSPARENT = 0x00000020
        hwnd = self.root.winfo_id()
        styles = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE,
                                            styles | WS_EX_LAYERED | WS_EX_TRANSPARENT)

    def _toggle_visibility(self, _evt=None):
        self.visible = not self.visible
        self.root.attributes("-alpha", 1.0 if self.visible else 0.0)

    def _tick(self):
        self.canvas.delete("all")

        # Draw screen border (light)
        self.canvas.create_rectangle(1, 1, self.zones.sw-2, self.zones.sh-2,
                                     outline="#888888", width=1)

        # Rectangles
        for (x, y, w, h) in self.zones.rects:
            self.canvas.create_rectangle(x, y, x+w, y+h,
                                         outline=self.color_rect, width=self.line_width)

        # Polygons
        for pts in self.zones.polys:
            flat = [c for xy in pts for c in xy]
            self.canvas.create_polygon(flat, outline=self.color_poly,
                                       fill="", width=self.line_width)
            if self.show_centroids:
                cx, cy = self._poly_centroid(pts)
                r = 3
                self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r,
                                        outline=self.color_poly, width=1)

        self.root.after(self.refresh_ms, self._tick)

    @staticmethod
    def _poly_centroid(poly):
        # Same centroid logic as before (works for simple polygons)
        A = 0.0
        cx = 0.0
        cy = 0.0
        n = len(poly)
        for i in range(n):
            x1, y1 = poly[i]
            x2, y2 = poly[(i+1) % n]
            cross = x1*y2 - x2*y1
            A += cross
            cx += (x1 + x2) * cross
            cy += (y1 + y2) * cross
        A *= 0.5
        if A == 0.0:
            xs, ys = zip(*poly)
            return sum(xs)/n, sum(ys)/n
        cx /= (6.0 * A)
        cy /= (6.0 * A)
        return cx, cy




if __name__ == "__main__":
    # Example usage
    poly1 = [(100, 100), (200, 100), (200, 200), (100, 200)]
    polys = [poly1]
    overlay = ZoneOverlay(polys, click_through=True)  # F8 hide/show, Esc close
