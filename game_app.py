# game_app.py
# Main GUI controller for the Spot-the-Difference game.

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2

from image_processor import ImageProcessor


class GameApp:
    """
    GUI controller (MVC "Controller") for the Spot-the-Difference game.

    Responsibilities:
    - Build and manage the Tkinter UI
    - Delegate image processing to ImageProcessor
    - Translate player clicks into game events
    - Keep score labels up to date

    WHY a class instead of procedural code:
    - Groups all related state (processor, labels, canvas, counters) together
    - Tkinter callbacks can reference self cleanly
    - Easy to reset/restart a game without rebuilding the whole window
    """

    # Maximum wrong clicks before the game ends
    MAX_MISTAKES = 3

    # Canvas half-width — left half = original, right half = modified
    DISPLAY_SIZE = 400

    def __init__(self, root):
        """
        Build the UI and initialise game state.

        Parameters
        ----------
        root : tk.Tk – the top-level Tkinter window
        """
        # ── Game state ────────────────────────────────────────────────
        self.processor = None   # set in load_image(); guards on_click / reveal
        self.mistakes  = 0

        # Scaling factors: image pixels → display pixels (set in display_images)
        self.scale_x = 1.0
        self.scale_y = 1.0

        # ── Title ──────────────────────────────────────────────────────
        tk.Label(
            root,
            text="🎯 Spot The Difference",
            font=("Arial", 20, "bold"),
        ).pack(pady=10)

        # ── Subtitle ───────────────────────────────────────────────────
        tk.Label(
            root,
            text="Find all 5 differences in the image",
            font=("Arial", 12),
        ).pack(pady=5)

        # ── Instructions ───────────────────────────────────────────────
        tk.Label(
            root,
            text=(
                "📌 Instructions:\n"
                "  • Click on differences in the RIGHT image\n"
                f"  • You have {self.MAX_MISTAKES} mistakes allowed\n"
                "  • Use 'Reveal' if stuck\n"
                "  • Find all differences to win"
            ),
            justify="left",
            font=("Arial", 10),
            bg="#f0f0f0",
            padx=10,
            pady=10,
        ).pack(pady=10)

        # ── Buttons ────────────────────────────────────────────────────
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        tk.Button(
            button_frame,
            text="Load Image",
            command=self.load_image,
            width=15,
        ).grid(row=0, column=0, padx=5)

        tk.Button(
            button_frame,
            text="Reveal Differences",
            command=self.reveal_differences,
            width=18,
        ).grid(row=0, column=1, padx=5)

        # ── Status labels ──────────────────────────────────────────────
        self.status_label = tk.Label(
            root,
            text="Status: Ready — load an image to start",
            font=("Arial", 12, "bold"),
        )
        self.status_label.pack(pady=5)

        self.remaining_label = tk.Label(root, text="Remaining: —")
        self.remaining_label.pack()

        self.mistake_label = tk.Label(root, text="Mistakes: 0")
        self.mistake_label.pack()

        # ── Canvas ─────────────────────────────────────────────────────
        # Width = 2 × DISPLAY_SIZE (left = original, right = modified)
        canvas_width = self.DISPLAY_SIZE * 2
        self.canvas = tk.Canvas(root, width=canvas_width, height=self.DISPLAY_SIZE, bg="white")
        self.canvas.pack(pady=10)
        self.canvas.bind("<Button-1>", self.on_click)

    # ──────────────────────────────────────────────────────────────────

    def load_image(self):
        """
        Open a file dialog, load the chosen image, and start a new game.

        WHY we reset state here rather than in __init__:
        - Allows the player to load a new image mid-session without
          restarting the application.
        """
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if not file_path:
            return  # user cancelled — do nothing

        # Reset counters for the new game
        self.mistakes = 0

        try:
            self.processor = ImageProcessor(file_path)
            self.processor.generate_differences()
        except ValueError as err:
            messagebox.showerror("Load Error", str(err))
            self.processor = None
            return

        self.display_images()
        self.update_labels()
        self.status_label.config(text="Status: Game in progress")

    # ──────────────────────────────────────────────────────────────────

    def display_images(self):
        """
        Convert OpenCV images to Tkinter-compatible format and draw them.

        Conversion chain:
          OpenCV  BGR  →  PIL RGB  →  PIL resize  →  ImageTk.PhotoImage

        WHY store tk_original / tk_modified as instance attributes:
        - Tkinter's canvas does NOT keep a reference to PhotoImage objects.
          Without self.tk_*, the garbage collector destroys them immediately
          and the canvas shows a blank grey rectangle.

        WHY compute scale_x / scale_y:
        - The images are shrunk to DISPLAY_SIZE × DISPLAY_SIZE for display.
          Click coordinates arrive in display-pixel space; we must scale them
          back to image-pixel space before checking Difference.contains_point.
        """
        original_bgr, modified_bgr = self.processor.get_images()

        img_h, img_w = original_bgr.shape[:2]

        # scale factors: image-pixels per display-pixel
        self.scale_x = img_w / self.DISPLAY_SIZE
        self.scale_y = img_h / self.DISPLAY_SIZE

        def to_tk(bgr_img):
            rgb = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
            pil = Image.fromarray(rgb).resize(
                (self.DISPLAY_SIZE, self.DISPLAY_SIZE), Image.LANCZOS
            )
            return ImageTk.PhotoImage(pil)

        self.tk_original = to_tk(original_bgr)
        self.tk_modified  = to_tk(modified_bgr)

        self.canvas.delete("all")
        self.canvas.create_image(0,                  0, anchor="nw", image=self.tk_original)
        self.canvas.create_image(self.DISPLAY_SIZE,  0, anchor="nw", image=self.tk_modified)

    # ──────────────────────────────────────────────────────────────────

    def on_click(self, event):
        """
        Handle a canvas click.

        Logic:
        1. Ignore clicks if no image is loaded or the game is already over.
        2. Ignore clicks on the LEFT (original) panel — the player must click
           on the RIGHT (modified) panel.
        3. Convert display coordinates → image coordinates using scale factors.
        4. Check every unfound Difference; mark the first hit found.
        5. If nothing was hit, increment mistakes.
        6. Refresh labels and check win/lose conditions.
        """
        if self.processor is None:
            return  # no image loaded yet

        if self.mistakes >= self.MAX_MISTAKES:
            return  # game already lost

        x_display, y_display = event.x, event.y

        # Only clicks on the right (modified) half are valid
        if x_display < self.DISPLAY_SIZE:
            return

        # Convert from display-pixel space to image-pixel space
        x_img = (x_display - self.DISPLAY_SIZE) * self.scale_x
        y_img =  y_display                       * self.scale_y

        hit = False
        for diff in self.processor.get_differences():
            if not diff.found and diff.contains_point(x_img, y_img):
                diff.mark_found()
                self._draw_circle(diff, color="green")
                hit = True
                break   # one click = one difference at most

        if not hit:
            self.mistakes += 1

        self.update_labels()
        self._check_game_status()

    # ──────────────────────────────────────────────────────────────────

    def _draw_circle(self, diff, color="green"):
        """
        Draw a circle around a difference on BOTH canvas panels.

        The circle centre is computed in image-pixel space, then converted
        back to display-pixel space for drawing.

        WHY we mark both panels:
        - Helps the player compare the two images side by side after finding
          a difference.

        Parameters
        ----------
        diff  : Difference
        color : str – Tkinter colour string (default "green" for found,
                      "blue" for revealed)
        """
        # Centre of the difference in image-pixel space
        cx_img = diff.x + diff.width  / 2
        cy_img = diff.y + diff.height / 2

        # Convert to display-pixel space
        cx = cx_img / self.scale_x
        cy = cy_img / self.scale_y
        r  = 22  # circle radius in display pixels

        # Left panel (original image) — no x offset
        self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                outline=color, width=2)

        # Right panel (modified image) — shifted by DISPLAY_SIZE
        ox = self.DISPLAY_SIZE
        self.canvas.create_oval(cx + ox - r, cy - r, cx + ox + r, cy + r,
                                outline=color, width=2)

    # ──────────────────────────────────────────────────────────────────

    def update_labels(self):
        """Refresh the 'Remaining' and 'Mistakes' counters in the UI."""
        if self.processor is None:
            return
        remaining = sum(1 for d in self.processor.get_differences() if not d.found)
        self.remaining_label.config(text=f"Remaining: {remaining}")
        self.mistake_label.config(
            text=f"Mistakes: {self.mistakes} / {self.MAX_MISTAKES}"
        )

    # ──────────────────────────────────────────────────────────────────

    def _check_game_status(self):
        """
        Evaluate win and lose conditions after every click.

        Win  : all differences found
        Lose : mistake count reaches MAX_MISTAKES
        """
        remaining = sum(1 for d in self.processor.get_differences() if not d.found)

        if remaining == 0:
            self.status_label.config(text="Status: You won! 🎉")
            messagebox.showinfo("Well done!", "You found all the differences!")

        elif self.mistakes >= self.MAX_MISTAKES:
            self.status_label.config(text="Status: Game over ❌")
            messagebox.showwarning("Game Over", "Too many mistakes — better luck next time!")

    # ──────────────────────────────────────────────────────────────────

    def reveal_differences(self):
        """
        Reveal all remaining (unfound) differences in blue.

        WHY blue instead of green:
        - Green circles mark differences the player found themselves.
        - Blue circles indicate differences revealed by the hint — keeping
          them visually distinct preserves the sense of achievement.
        """
        if self.processor is None:
            messagebox.showinfo("No image", "Load an image first.")
            return

        revealed = 0
        for diff in self.processor.get_differences():
            if not diff.found:
                self._draw_circle(diff, color="blue")
                revealed += 1

        if revealed == 0:
            messagebox.showinfo("All found", "You already found every difference!")
