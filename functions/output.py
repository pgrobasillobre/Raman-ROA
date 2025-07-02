import sys

# -------------------------------------------------------------------------------------
def error(error_message):
   """
   Prints an error message and terminates execution.

   Args:
       error_message (str): The error message to be displayed.

   Returns:
       None: The function exits the program.
   """

   print("")
   print("")
   print("   ERROR: " + error_message)
   print("")
   print("")
   sys.exit()
# -------------------------------------------------------------------------------------