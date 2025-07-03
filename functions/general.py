import argparse
import sys
import os

from functions import output

# -------------------------------------------------------------------------------------
def read_command_line(argv, inp):
    parser = argparse.ArgumentParser(description="Raman/ROA Data Extraction")
    parser.add_argument('-w', choices=['raman', 'roa'], required=True, help="Type of analysis: raman or roa")
    parser.add_argument('-i', dest='ams_file', required=True, help="AMS file to process")
    parser.add_argument('-freqmin', type=float, required=True, help="Minimum frequency (nm)")
    parser.add_argument('-freqmax', type=float, required=True, help="Maximum frequency (nm)")
    parser.add_argument('-incoming_field_ev', type=float, required=True, help="Incoming field energy (eV)")
    parser.add_argument('-pol', choices=['x', 'y', 'z', 'back'], help="Polarization for ROA (required for roa)")
    parser.add_argument('-norm', action='store_true', help="Apply normalization (optional)")


    args = parser.parse_args(argv[1:])

    # Enforce -pol required for ROA
    if args.w == 'roa' and args.pol is None:
        parser.error("argument -pol is required when -w roa is selected.")

    inp.raman = args.w == 'raman'
    inp.roa = args.w == 'roa'
    inp.ams_file = args.ams_file
    inp.norm = args.norm
    inp.pol = args.pol if inp.roa else None
    inp.freq_min = args.freqmin
    inp.freq_max = args.freqmax
    inp.incoming_field_ev = args.incoming_field_ev

    # Check if the AMS file exists
    check_file_exists(inp.ams_file)
# -------------------------------------------------------------------------------------
def check_file_exists(infile):
   """
   Checks if a given file exists.

   Args:
       infile (str): Path to the input file.

   Returns:
       None: Raises an error if the file is not found.
   """

   if (not os.path.exists(infile)): output.error('file "' + infile + '" not found')
# -------------------------------------------------------------------------------------
