"""
image_processor.py
Handles all image loading and modification using OpenCV.
Demonstrates OOP: encapsulation, constructors, methods.
"""

import cv2
import numpy as np
import random


class DifferenceRegion:
    """Represents a single difference region on the modified image."""

    def __init__(self, x: int, y: int, w: int, h: int, diff_type: str):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.diff_type = diff_type
        self.found = False

    def center(self):
        return (self.x + self.w // 2, self.y + self.h // 2)

    def contains_point(self, px: int, py: int, tolerance: int = 30) -> bool:
        """Check if a point is within the region (with tolerance)."""
        cx, cy = self.center()
        return abs(px - cx) <= (self.w // 2 + tolerance) and abs(py - cy) <= (self.h // 2 + tolerance)

    def __repr__(self):
        return f"DifferenceRegion(type={self.diff_type}, x={self.x}, y={self.y}, found={self.found})"


class ImageProcessor:
    """
    Loads an original image, creates a clone, and applies 5 random differences.
    Uses OpenCV for all image manipulation.
    Demonstrates: encapsulation, constructor, methods.
    """

    NUM_DIFFERENCES = 5
    MIN_REGION_SIZE = 40
    MAX_REGION_SIZE = 80

    # Available alteration types
    ALTERATION_TYPES = ["colour_shift", "blur", "brightness", "invert_region", "noise"]

    def __init__(self):
        self.original_bgr = None
        self.modified_bgr = None
        self.difference_regions: list[DifferenceRegion] = []
        self.image_path = None

    def load_image(self, path: str) -> bool:
        """Load image from disk and generate modified version."""
        img = cv2.imread(path)
        if img is None:
            return False
        self.image_path = path
        # Resize to a manageable display size
        img = self._resize_image(img, max_width=600, max_height=500)
        self.original_bgr = img.copy()
        self.modified_bgr, self.difference_regions = self._generate_differences(img.copy())
        return True

    def _resize_image(self, img: np.ndarray, max_width: int, max_height: int) -> np.ndarray:
        h, w = img.shape[:2]
        scale = min(max_width / w, max_height / h, 1.0)
        if scale < 1.0:
            new_w, new_h = int(w * scale), int(h * scale)
            img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        return img

    def _generate_differences(self, modified: np.ndarray):
        """Place exactly 5 non-overlapping differences on the modified image."""
        h, w = modified.shape[:2]
        regions: list[DifferenceRegion] = []
        alteration_types = self.ALTERATION_TYPES.copy()
        random.shuffle(alteration_types)
        # Ensure at least 3 distinct types used (cycle if needed)
        types_to_use = []
        for i in range(self.NUM_DIFFERENCES):
            types_to_use.append(alteration_types[i % len(alteration_types)])
        random.shuffle(types_to_use)

        attempts = 0
        while len(regions) < self.NUM_DIFFERENCES and attempts < 500:
            attempts += 1
            rw = random.randint(self.MIN_REGION_SIZE, self.MAX_REGION_SIZE)
            rh = random.randint(self.MIN_REGION_SIZE, self.MAX_REGION_SIZE)
            rx = random.randint(0, w - rw - 1)
            ry = random.randint(0, h - rh - 1)

            # Check no overlap with existing regions (with padding)
            pad = 15
            overlap = False
            for existing in regions:
                if not (rx + rw + pad <= existing.x or
                        rx >= existing.x + existing.w + pad or
                        ry + rh + pad <= existing.y or
                        ry >= existing.y + existing.h + pad):
                    overlap = True
                    break
            if overlap:
                continue

            diff_type = types_to_use[len(regions)]
            modified = self._apply_alteration(modified, rx, ry, rw, rh, diff_type)
            regions.append(DifferenceRegion(rx, ry, rw, rh, diff_type))

        return modified, regions

    def _apply_alteration(self, img: np.ndarray, x: int, y: int, w: int, h: int, diff_type: str) -> np.ndarray:
        """Apply one of 5 alteration types to a rectangular region."""
        roi = img[y:y+h, x:x+w].copy()

        if diff_type == "colour_shift":
            # Shift hue in HSV space
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV).astype(np.int32)
            shift = random.choice([40, -40, 60, -60])
            hsv[:, :, 0] = (hsv[:, :, 0] + shift) % 180
            hsv = np.clip(hsv, 0, 255).astype(np.uint8)
            roi = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        elif diff_type == "blur":
            ksize = random.choice([11, 15, 19])
            roi = cv2.GaussianBlur(roi, (ksize, ksize), 0)

        elif diff_type == "brightness":
            factor = random.choice([50, -50, 70, -70])
            roi = np.clip(roi.astype(np.int32) + factor, 0, 255).astype(np.uint8)

        elif diff_type == "invert_region":
            roi = cv2.bitwise_not(roi)
            # Blend slightly so it's not too obvious
            original_roi = img[y:y+h, x:x+w].copy()
            roi = cv2.addWeighted(roi, 0.6, original_roi, 0.4, 0)

        elif diff_type == "noise":
            noise = np.random.randint(-40, 40, roi.shape, dtype=np.int32)
            roi = np.clip(roi.astype(np.int32) + noise, 0, 255).astype(np.uint8)

        img[y:y+h, x:x+w] = roi
        return img

    def draw_circle_on_image(self, img: np.ndarray, region: DifferenceRegion,
                              color: tuple, thickness: int = 3) -> np.ndarray:
        """Draw a circle around a difference region on a copy of the image."""
        result = img.copy()
        cx, cy = region.center()
        radius = max(region.w, region.h) // 2 + 10
        cv2.circle(result, (cx, cy), radius, color, thickness)
        return result

    def get_original_display(self) -> np.ndarray:
        return self.original_bgr.copy() if self.original_bgr is not None else None

    def get_modified_display(self) -> np.ndarray:
        return self.modified_bgr.copy() if self.modified_bgr is not None else None

    def get_image_size(self):
        if self.original_bgr is not None:
            h, w = self.original_bgr.shape[:2]
            return w, h
        return 0, 0
