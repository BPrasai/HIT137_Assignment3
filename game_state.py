"""
game_state.py
Manages all game logic and state.
Demonstrates: encapsulation, constructors, methods, class interaction.
"""

from image_processor import ImageProcessor, DifferenceRegion
import numpy as np


class GameState:
    """
    Manages the state of the current game round:
    - tracks found/unfound differences
    - counts mistakes
    - accumulates score across rounds
    Demonstrates: encapsulation, constructor, methods.
    """

    MAX_MISTAKES = 3

    def __init__(self):
        self.image_processor = ImageProcessor()
        self.mistakes = 0
        self.total_found = 0          # cumulative across all images
        self.current_found = 0        # found in this round
        self.images_completed = 0
        self.game_over = False        # True when 3 mistakes reached
        self.all_found = False        # True when all 5 found
        self.revealed = False
        # Rendered image arrays (with circles drawn)
        self._original_display: np.ndarray = None
        self._modified_display: np.ndarray = None

    # Properties 
    @property
    def is_loaded(self) -> bool:
        return self.image_processor.original_bgr is not None

    @property
    def differences(self) -> list[DifferenceRegion]:
        return self.image_processor.difference_regions

    @property
    def remaining(self) -> int:
        return sum(1 for d in self.differences if not d.found)

    @property
    def can_click(self) -> bool:
        return self.is_loaded and not self.game_over and not self.all_found and not self.revealed

    #  Image loading 
    def load_image(self, path: str) -> bool:
        ok = self.image_processor.load_image(path)
        if ok:
            self.mistakes = 0
            self.current_found = 0
            self.game_over = False
            self.all_found = False
            self.revealed = False
            self._refresh_display()
        return ok

    # Click handling 
    def handle_click(self, px: int, py: int) -> str:
        """
        Process a click on the modified image.
        Returns: 'found', 'already_found', 'mistake', 'max_mistakes', 'no_image'
        """
        if not self.is_loaded:
            return "no_image"
        if not self.can_click:
            return "blocked"

        # Check if click hits any unfound region
        for region in self.differences:
            if not region.found and region.contains_point(px, py):
                region.found = True
                self.current_found += 1
                self.total_found += 1
                self._draw_circle_found(region)
                if self.remaining == 0:
                    self.all_found = True
                    self.images_completed += 1
                return "found"

        # Miss
        self.mistakes += 1
        if self.mistakes >= self.MAX_MISTAKES:
            self.game_over = True
            return "max_mistakes"
        return "mistake"

    #  Reveal 
    def reveal_all(self):
        """Mark all unfound differences with blue circles."""
        if not self.is_loaded:
            return
        for region in self.differences:
            if not region.found:
                self._draw_circle_revealed(region)
        self.revealed = True

    #  Display helpers 
    def _refresh_display(self):
        self._original_display = self.image_processor.get_original_display()
        self._modified_display = self.image_processor.get_modified_display()

    def _draw_circle_found(self, region: DifferenceRegion):
        RED = (0, 0, 255)   # BGR
        ip = self.image_processor
        self._original_display = ip.draw_circle_on_image(self._original_display, region, RED)
        self._modified_display = ip.draw_circle_on_image(self._modified_display, region, RED)

    def _draw_circle_revealed(self, region: DifferenceRegion):
        BLUE = (255, 0, 0)  # BGR
        ip = self.image_processor
        self._original_display = ip.draw_circle_on_image(self._original_display, region, BLUE)
        self._modified_display = ip.draw_circle_on_image(self._modified_display, region, BLUE)

    def get_original_display(self) -> np.ndarray:
        return self._original_display

    def get_modified_display(self) -> np.ndarray:
        return self._modified_display
