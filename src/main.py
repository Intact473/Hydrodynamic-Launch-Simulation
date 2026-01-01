import sys
sys.dont_write_bytecode = True

from view import window
from physic import formulas


if __name__ == "__main__":
    try:
        window.run_window(start=formulas.start)
    except ValueError as window_exception:
        print("Error while creating the window: ", window_exception)