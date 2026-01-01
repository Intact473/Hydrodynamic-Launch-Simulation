import sys
sys.dont_write_bytecode = True

from view import window
from physic import formulas

"""
Main entry point for the Water Rocket Simulation application.
Initializes the GUI window and handles exceptions during startup.
"""

if __name__ == "__main__":
    """
    Start the main application window.
    """
    try:
        window.run_window(start=formulas.start)
    except ValueError as window_exception:
        print("Error while creating the window: ", window_exception)