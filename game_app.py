"""
game_app.py
Main Tkinter GUI for the Spot the Difference game.
Demonstrates: OOP, inheritance (GameApp extends BaseApp), polymorphism,
              class interaction, encapsulation.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import cv2
import numpy as np
from PIL import Image, ImageTk

from game_state import GameState


# ─── Base class (inheritance) ────────────────────────────────────────────────
class BaseApp:
    """
    Abstract base class that owns the Tk root window.
    Demonstrates inheritance — SpotTheDifferenceApp extends this.
    """

    def __init__(self, title: str = "App", width: int = 1300, height: int = 700):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(True, True)
        self.root.configure(bg="#1e1e2e")

    def run(self):
        self.root.mainloop()

    def _quit(self):
        self.root.destroy()


# ─── Main application (polymorphism via method overriding) ───────────────────
class SpotTheDifferenceApp(BaseApp):
    """
    Full Spot-the-Difference desktop application.
    Overrides / extends BaseApp with game-specific UI and logic.
    Demonstrates: inheritance, polymorphism, class interaction with GameState.
    """

    # Colours
    BG        = "#1e1e2e"
    PANEL_BG  = "#2a2a3e"
    ACCENT    = "#89b4fa"
    GREEN     = "#a6e3a1"
    RED       = "#f38ba8"
    YELLOW    = "#f9e2af"
    TEXT      = "#cdd6f4"
    SUB_TEXT  = "#6c7086"

    def __init__(self):
        super().__init__(title="🔍 Spot the Difference", width=1340, height=760)
        self.state = GameState()
        self._build_ui()

    # ── UI construction ──────────────────────────────────────────────────────
    def _build_ui(self):
        # Top toolbar
        toolbar = tk.Frame(self.root, bg=self.PANEL_BG, pady=8)
        toolbar.pack(fill=tk.X, side=tk.TOP)

        tk.Button(toolbar, text="📂  Load Image", command=self._load_image,
                  bg=self.ACCENT, fg="#1e1e2e", font=("Segoe UI", 11, "bold"),
                  relief=tk.FLAT, padx=14, pady=6, cursor="hand2"
                  ).pack(side=tk.LEFT, padx=(14, 6))

        tk.Button(toolbar, text="👁  Reveal All", command=self._reveal_all,
                  bg=self.YELLOW, fg="#1e1e2e", font=("Segoe UI", 11, "bold"),
                  relief=tk.FLAT, padx=14, pady=6, cursor="hand2"
                  ).pack(side=tk.LEFT, padx=6)

        tk.Button(toolbar, text="✖  Quit", command=self._quit,
                  bg=self.RED, fg="#1e1e2e", font=("Segoe UI", 11, "bold"),
                  relief=tk.FLAT, padx=14, pady=6, cursor="hand2"
                  ).pack(side=tk.RIGHT, padx=14)

        # Status bar
        status_frame = tk.Frame(self.root, bg=self.PANEL_BG, pady=6)
        status_frame.pack(fill=tk.X, side=tk.TOP)

        self._var_remaining  = tk.StringVar(value="Remaining: –")
        self._var_mistakes   = tk.StringVar(value="Mistakes: 0 / 3")
        self._var_total      = tk.StringVar(value="Total Found: 0")
        self._var_images     = tk.StringVar(value="Images Completed: 0")
        self._var_status     = tk.StringVar(value="Load an image to start playing!")

        for var, col in [
            (self._var_remaining, self.ACCENT),
            (self._var_mistakes,  self.RED),
            (self._var_total,     self.GREEN),
            (self._var_images,    self.YELLOW),
        ]:
            tk.Label(status_frame, textvariable=var, bg=self.PANEL_BG,
                     fg=col, font=("Segoe UI", 11, "bold"), padx=20
                     ).pack(side=tk.LEFT)

        self._lbl_status = tk.Label(status_frame, textvariable=self._var_status,
                                    bg=self.PANEL_BG, fg=self.TEXT,
                                    font=("Segoe UI", 11), padx=20)
        self._lbl_status.pack(side=tk.RIGHT, padx=14)

        # Main canvas area
        canvas_container = tk.Frame(self.root, bg=self.BG)
        canvas_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        # Left image (original – no clicks)
        left_frame = tk.Frame(canvas_container, bg=self.PANEL_BG, bd=2, relief=tk.FLAT)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        tk.Label(left_frame, text="Original", bg=self.PANEL_BG,
                 fg=self.SUB_TEXT, font=("Segoe UI", 10)).pack(pady=(4, 0))
        self._canvas_orig = tk.Canvas(left_frame, bg=self.BG,
                                      highlightthickness=0, cursor="arrow")
        self._canvas_orig.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # Right image (modified – clickable)
        right_frame = tk.Frame(canvas_container, bg=self.PANEL_BG, bd=2, relief=tk.FLAT)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        tk.Label(right_frame, text="Modified  (click here!)", bg=self.PANEL_BG,
                 fg=self.ACCENT, font=("Segoe UI", 10, "bold")).pack(pady=(4, 0))
        self._canvas_mod = tk.Canvas(right_frame, bg=self.BG,
                                     highlightthickness=0, cursor="crosshair")
        self._canvas_mod.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self._canvas_mod.bind("<Button-1>", self._on_canvas_click)

        # Placeholder text
        self._draw_placeholder()

    def _draw_placeholder(self):
        for canvas in (self._canvas_orig, self._canvas_mod):
            canvas.delete("all")
            canvas.create_text(300, 240, text="No image loaded",
                                fill=self.SUB_TEXT, font=("Segoe UI", 16))

    # ── Image loading ────────────────────────────────────────────────────────
    def _load_image(self):
        path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp"),
                       ("All files", "*.*")]
        )
        if not path:
            return
        ok = self.state.load_image(path)
        if not ok:
            messagebox.showerror("Error", "Could not load image.\nPlease choose a valid JPG, PNG, or BMP file.")
            return
        self._refresh_canvases()
        self._update_status_bar()
        self._var_status.set("Find the 5 differences! Click on the modified image.")

    # ── Click handler ────────────────────────────────────────────────────────
    def _on_canvas_click(self, event):
        if not self.state.can_click:
            return

        # Map canvas coords → image coords
        px, py = self._canvas_to_image_coords(event.x, event.y)
        result = self.state.handle_click(px, py)

        self._refresh_canvases()
        self._update_status_bar()

        if result == "found":
            if self.state.all_found:
                self._lbl_status.configure(fg=self.GREEN)
                self._var_status.set("🎉 All 5 differences found! Load a new image to continue.")
                messagebox.showinfo("Well done!", "You found all 5 differences!\nLoad another image to keep playing.")
            else:
                self._lbl_status.configure(fg=self.GREEN)
                self._var_status.set(f"✅ Correct! {self.state.remaining} difference(s) remaining.")

        elif result == "mistake":
            self._lbl_status.configure(fg=self.YELLOW)
            self._var_status.set(f"❌ Wrong spot! {self.state.MAX_MISTAKES - self.state.mistakes} guess(es) left.")

        elif result == "max_mistakes":
            self._lbl_status.configure(fg=self.RED)
            self._var_status.set(
                f"💀 Too many mistakes! {self.state.current_found}/5 found. Load a new image to restart."
            )
            messagebox.showwarning(
                "Game Over",
                f"You made 3 mistakes!\n"
                f"You found {self.state.current_found} out of 5 differences.\n\n"
                "Load a new image to restart."
            )

    # ── Reveal ───────────────────────────────────────────────────────────────
    def _reveal_all(self):
        if not self.state.is_loaded:
            messagebox.showinfo("No image", "Please load an image first.")
            return
        if self.state.all_found or self.state.revealed:
            return
        self.state.reveal_all()
        self._refresh_canvases()
        self._update_status_bar()
        self._lbl_status.configure(fg=self.ACCENT)
        self._var_status.set("🔵 All differences revealed. Load a new image to restart.")

    # ── Rendering helpers ────────────────────────────────────────────────────
    def _refresh_canvases(self):
        orig_arr = self.state.get_original_display()
        mod_arr  = self.state.get_modified_display()
        if orig_arr is None or mod_arr is None:
            return
        self._render_on_canvas(self._canvas_orig, orig_arr)
        self._render_on_canvas(self._canvas_mod,  mod_arr)

    def _render_on_canvas(self, canvas: tk.Canvas, bgr_array: np.ndarray):
        canvas.update_idletasks()
        cw = canvas.winfo_width()
        ch = canvas.winfo_height()
        if cw < 10 or ch < 10:
            cw, ch = 580, 520

        # Convert BGR → RGB
        rgb = cv2.cvtColor(bgr_array, cv2.COLOR_BGR2RGB)
        ih, iw = rgb.shape[:2]

        # Scale to fit canvas while preserving aspect ratio
        scale = min(cw / iw, ch / ih)
        nw, nh = int(iw * scale), int(ih * scale)
        rgb_resized = cv2.resize(rgb, (nw, nh), interpolation=cv2.INTER_AREA)

        pil_img = Image.fromarray(rgb_resized)
        tk_img  = ImageTk.PhotoImage(pil_img)

        canvas.delete("all")
        # Centre the image
        ox = (cw - nw) // 2
        oy = (ch - nh) // 2
        canvas.create_image(ox, oy, anchor=tk.NW, image=tk_img)
        canvas._tk_img = tk_img  # prevent garbage collection
        # Store offset + scale for click mapping
        canvas._img_offset = (ox, oy)
        canvas._img_scale  = scale
        canvas._img_size   = (iw, ih)

    def _canvas_to_image_coords(self, cx: int, cy: int):
        """Map a click on the modified canvas to original image coordinates."""
        canvas = self._canvas_mod
        if not hasattr(canvas, "_img_offset"):
            return cx, cy
        ox, oy = canvas._img_offset
        scale  = canvas._img_scale
        ix = int((cx - ox) / scale)
        iy = int((cy - oy) / scale)
        return ix, iy

    def _update_status_bar(self):
        self._var_remaining.set(f"Remaining: {self.state.remaining if self.state.is_loaded else '–'}")
        self._var_mistakes.set(f"Mistakes: {self.state.mistakes} / {GameState.MAX_MISTAKES}")
        self._var_total.set(f"Total Found: {self.state.total_found}")
        self._var_images.set(f"Images Completed: {self.state.images_completed}")
