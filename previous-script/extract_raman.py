import matplotlib.pyplot as plt
import numpy as np
import sys
import os

#
# PURPOSE: Extract RAMAN convoluted spectra 
#
# EXECUTION details: python3 extract_raman.py -h 
#

# -------------- Parameters ---------------
fwhm    = 20.0 # cm^{-1} Taken from: https://doi.org/10.1021/jp502107f
freqmin = 500 
freqmax = 1700

incoming_field_ev = 3.41 # eV
ev_to_wavenumbers = 8065.54429 # eV * fattore = cm^{-1}
# -----------------------------------------


# -------------- Parameters ---------------
raman_first_line = ' Frequency (New) [cm-1] | Raman Int. [A^4/amu]'
# -----------------------------------------


# --------------- Functions ---------------
def error(message):
   print('')
   print('')
   print(f'   {message}')
   print('')
   print('')
   sys.exit()
# -----------------------------------------
def check_file_exists(infile):
   if (not os.path.exists(infile)): error(f'File "{infile}" is not in current folder.')
# -----------------------------------------
def conv_stick(freqs,freq_peaks,int_peaks):
    spectrum = np.zeros(np.shape(freqs))
    for peak in range(len(freq_peaks)):
        spectrum = spectrum + (fwhm/((freqs-freq_peaks[peak])**2+fwhm)*int_peaks[peak])
    return spectrum
# -----------------------------------------




# --------------- Check inputs ---------------
try_help  = 'python3 extract_raman.py -f adf_file [optional: -norm/-sticks]'

normalize = False
sticks    = False

if (sys.argv[1]!='-h' and len(sys.argv) <3):
   error(f'Not enough inputs parsed. --> Try: {try_help}')

elif (sys.argv[1]=='-h'):
   error(f'Execution: {try_help}')

elif (sys.argv[1]!='-f'):
   error(f'Option "{sys.argv[1]}" not supported. --> Try: {try_help}')

for i in sys.argv:
   if i=='-norm': normalize = True
   if i=='-sticks': sticks  = True 

logfile = sys.argv[2]
check_file_exists(logfile)
# --------------------------------------------


# --------------- Read RAMAN -----------------
freq_cm = []
raman_int = []

raman_found    = False
sticks_found = False

with open(logfile,'r') as f:
   for line in f:

      if (raman_found and sticks_found and len(line) == 1): break

      if (raman_found and sticks_found):
         freq_cm.append(float(line.split()[2]))
         raman_int.append(float(line.split()[3]))

      if (line.startswith(raman_first_line)):     raman_found = True
      if ((raman_found) and line.startswith(' -')): sticks_found = True
# --------------------------------------------


# ----- Generate Spectrum, Plot, and Save ----
# I_corr = I * ( wavenumber_campo_incidente - wavenumber_modo_normale )^4 / wavenumber_modo_normale
for i in range(len(raman_int)):
   raman_int[i] = raman_int[i] * (incoming_field_ev*ev_to_wavenumbers-freq_cm[i])**4/freq_cm[i]

freqs = np.linspace(freqmin,freqmax,freqmax-freqmin)
raman_spec = np.zeros([freqmax-freqmin])

raman_spec = conv_stick(freqs,freq_cm,raman_int)

if (normalize):
   raman_spec_abs = [abs(x) for x in raman_spec]
   norm = max(raman_spec_abs)

   for i in range(freqmax-freqmin):
      raman_spec[i] = raman_spec[i]/norm 

# Create the plot
plt.figure(figsize=(10, 6))
plt.plot(freqs, raman_spec, linestyle='-')

# Reverse the x-axis
plt.gca().invert_xaxis()

# Set the labels
plt.xlabel('Wavenumber (cm$^{-1}$)')
plt.ylabel('I$_R$ - I$_L$ (a.u.)')
if (normalize): plt.ylabel('I$_R$ - I$_L$ (arb. units)')

# Set the title (optional)
plt.title(f'RAMAN Spectrum')


plt.grid(True)

output_filename = f'RAMAN_spectrum.png'
if (normalize): output_filename = f'RAMAN_spectrum_NORM.png'

plt.savefig(output_filename, dpi=300, bbox_inches='tight')

plt.show()

output_csv = f'{logfile[:-4]}_RAMAN.csv'
if (normalize): output_csv = f'{logfile[:-4]}_RAMAN_NORM'
output_csv = output_csv + '.csv' 
with open (output_csv, 'w') as f:
   for x,y in zip(freqs,raman_spec):
      f.write(f'{x:25.16f}   {y:25.16f}  \n')
# --------------------------------------------


# --------- Save single point values ---------
if (sticks):
   output_csv = f'{logfile[:-4]}_RAMAN_STICKS.csv'
   with open (output_csv, 'w') as f:
      for x,y in zip(freq_cm,raman_int):
         f.write(f'{x:25.16f}   {y:25.16f}  \n')
# --------------------------------------------
