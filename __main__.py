import sys

from classes import input_class
from functions import general, output, process


# ============================================================================================================ #
#                                        Program by Pablo Grobas Illobre                                       #
#                                                                                                              #
#                                       Contact: pgrobasillobre@gmail.com                                      #
# ============================================================================================================ #


def main():
    """
    Main function to initialize input parameters and execute the appropriate Raman/ROA data extraction.

    Returns:
        None: Calls the relevant function based on the user's input.
    """
    try:
        # Initialize input class and parse command-line arguments
        inp = input_class.input_class()
        general.read_command_line(sys.argv, inp)

        # Select and execute the appropriate task
        if inp.raman:
            process.raman(inp)
        elif inp.roa:
            process.roa(inp)

    except Exception as e:
        output.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()