from difference import Difference

# Create a test difference
diff = Difference(50, 50, 100, 100, "color")

# Simulate clicks
print(diff.contains_point(60, 60))  # Expected: True
print(diff.contains_point(10, 10))  # Expected: False

diff.mark_found()
print(diff.found)  # Expected: True