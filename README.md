HIT137 Group Assignment 3
Group Name: DAN20
Group Members:
    Ayushma Pandey – S394814
    Bibek Prasai – S396542
    Tharaka Maduwantha Senevirathne Edirisinghe Arachchige – S396116
    Kritik Dahal – S395912

Description
    This project implements a desktop “Spot the Difference” game using:
        Object-Oriented Programming (OOP)
        Tkinter (GUI development)
        OpenCV (image processing)

    The application displays two nearly identical images side by side:
        The left image is the original.
        The right image is a modified version containing 5 hidden differences

    The player interacts with the modified image to identify all differences.

Core Features
    Gameplay Logic
        Exactly 5 differences are generated per image
        Differences are placed at random, non-overlapping locations
        Each session produces unique variations
        Players click on the modified image to locate differences
    Object-Oriented Design
        The system is structured using multiple classes to ensure clean separation of concerns:

    Key Classes:
        GameApp → Manages GUI, user interaction, and game flow
        ImageProcessor → Handles image loading and OpenCV modifications
        Difference → Represents individual difference regions
        GameState (optional enhancement) → Tracks score and mistakes
    
    OOP Principles Demonstrated:
        Encapsulation → Data and behavior grouped within classes
        Inheritance & Polymorphism → Used for extensibility of image effects
        Modularity → Separate files for each major component
        Class interaction → Coordinated communication between components
    Image Processing (OpenCV)
        When an image is loaded:
            The original image is duplicated
            5 random regions are generated
            Each region is modified using one of several techniques
        Supported Difference Types:
            Colour Shift → Subtle RGB variation
            Blur Effect → Local Gaussian blur
            Shape Overlay → Small shapes added to image
        Constraints:
            Differences do not overlap
            Changes are noticeable but not obvious
            All processing is done using OpenCV only
    Graphical User Interface (Tkinter)
        Interface Features:
            Load image from disk (JPG, PNG, BMP)
            Display images side by side
            Click-based interaction on modified image only
        Game Indicators:
            Remaining Differences Counter
            Mistake Counter (Max = 3)
        Game Rules
            ✔ Correct Guess:
            If a click is within a difference region:
            Difference is marked as found
            A red circle is drawn on both images
            ❌ Incorrect Guess:
            Mistake counter increases
            Maximum of 3 mistakes allowed
        Game Over:
            After 3 incorrect guesses:
            No further clicks allowed
            Player must load a new image
        Completion:
            When all 5 differences are found:
            Player is notified via popup/message
            Can load a new image to continue
        Reveal Feature
            A “Reveal Differences” button is available
            Displays all remaining differences using blue circles
            Ends the current round

Project Structure
    spot_the_difference/
    │
    ├── main.py
    ├── game_app.py
    ├── image_processor.py
    ├── difference.py
    ├── assets/
    ├── outputs/
    ├── README.md
    ├── github_link.txt
    └── .gitignore

▶ How to Run
    1. Install Dependencies
    pip install opencv-python pillow
    2. Run the Application
    python main.py
    3. Gameplay Steps
    Click “Load Image”
    Select an image file
    Click on the modified image to find differences
    Use “Reveal” if needed
    Load a new image to restart


🔗 GitHub Repository
(https://github.com/BPrasai/HIT137_Assignment3)

Summary
Fully interactive spot-the-difference game
Demonstrates strong OOP design principles
Uses OpenCV for dynamic image manipulation
Clean, modular, and scalable architecture
Randomised gameplay ensures replayability