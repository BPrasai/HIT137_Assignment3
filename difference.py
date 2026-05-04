class Difference:
    """
    This class represents a single difference region between
    the original and modified image.

    WHY this class exists:
    - Encapsulates all data about a difference
    - Avoids using raw tuples/dictionaries (better OOP practice)
    - Makes validation and tracking easier
    """

    def __init__(self, x, y, width, height, diff_type):
        """
        Constructor initializes a difference region.

        Parameters:
        - x, y: top-left corner of the region
        - width, height: size of the region
        - diff_type: type of modification applied (for extensibility)
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.diff_type = diff_type
        self.found = False  # Tracks whether user has already found this difference

    def contains_point(self, px, py):
        """
        Checks whether a given click (px, py) falls within this region.

        WHY we need this:
        - Used for validating user clicks
        - Encapsulates logic inside the class instead of scattering it

        We allow a small margin (tolerance) to make gameplay fair.
        """
        tolerance = 10  # pixels

        return (
            self.x - tolerance <= px <= self.x + self.width + tolerance and
            self.y - tolerance <= py <= self.y + self.height + tolerance
        )

    def mark_found(self):
        """
        Marks this difference as found.

        WHY method instead of direct assignment:
        - Encapsulation
        - Easier to extend later (e.g., logging, animations)
        """
        self.found = True