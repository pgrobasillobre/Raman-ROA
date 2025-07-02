import argparse
import sys

def read_command_line(argv, inp):
    parser = argparse.ArgumentParser(description="Raman/ROA Data Extraction")
    parser.add_argument('-w', choices=['raman', 'roa'], required=True, help="Type of analysis: raman or roa")
    parser.add_argument('-i', dest='adf_file', required=True, help="ADF file to process")
    parser.add_argument('-freqmin', type=float, required=True, help="Minimum frequency")
    parser.add_argument('-freqmax', type=float, required=True, help="Maximum frequency")
    parser.add_argument('-incoming_field_ev', type=float, required=True, help="Incoming field energy (eV)")
    parser.add_argument('-pol', choices=['x', 'y', 'z', 'back'], help="Polarization for ROA (required for roa)")
    parser.add_argument('-norm', action='store_true', help="Apply normalization (optional)")


    args = parser.parse_args(argv[1:])

    # Enforce -pol required for ROA
    if args.w == 'roa' and args.pol is None:
        parser.error("argument -pol is required when -w roa is selected.")

    inp.raman = args.w == 'raman'
    inp.roa = args.w == 'roa'
    inp.adf_file = args.adf_file
    inp.norm = args.norm
    inp.pol = args.pol if inp.roa else None
    inp.freqmin = args.freqmin
    inp.freqmax = args.freqmax
    inp.incoming_field_ev = args.incoming_field_ev