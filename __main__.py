import sys

from classes import input_class
from functions import general, output

# ============================================================================================================ #
#                                        Program by Pablo Grobas Illobre                                       #
#                                                                                                              #
#                                       Contact: pgrobasillobre@gmail.com                                      #
# ============================================================================================================ #


def main():
    """
    Main function to initialize input parameters and execute the appropriate data extraction.

    Returns:
        None: Calls the relevant function based on the user's input.
    """
    try:
        # Initialize input class and parse command-line arguments
        inp = input_class.input_class()
        general.read_command_line(sys.argv, inp)

        # Select and execute the appropriate task
        if inp.raman:
            pass
        elif inp.roa:
            pass

    except Exception as e:
        output.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()