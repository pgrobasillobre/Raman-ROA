import matplotlib.pyplot as plt
import numpy as np
import sys
import os

#
# PURPOSE: Extract ROA convoluted spectra 
#
# EXECUTION details: python3 extract_roa.py -h 
#

# -------------- Parameters ---------------
fwhm    = 20.0 # cm^{-1} Taken from: https://doi.org/10.1021/jp502107f
freqmin = 500 
freqmax = 1700

incoming_field_ev = 3.41 # eV
ev_to_wavenumbers = 8065.54429 # eV * fattore = cm^{-1}
# -----------------------------------------


# -------------- Parameters ---------------
roa_first_line = ' Frequency (New) [cm-1] |      Delta(0)'
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
try_help  = 'python3 extract_roa.py -pol {x/y/z/back} -f adf_file [optional: -norm/sticks/corr]'

normalize = False
sticks    = False
correct_ints = False
 
if (len(sys.argv)<1): 
   error('Please, select ROA polarization.')

elif (sys.argv[1]!='-h' and len(sys.argv) <4):
   error(f'Not enough inputs parsed. --> Try: {try_help}')

elif (sys.argv[1]=='-h'):
   error(f'Execution: {try_help}')

elif (sys.argv[1]!='-pol'):
   error(f'Option "{sys.argv[1]}" not supported. --> Try: {try_help}')

elif (sys.argv[3]!='-f'):
   error(f'Option "{sys.argv[3]}" not supported. --> Try: {try_help}')

elif (len(sys.argv)>7): 
   error(f'Too many inputs parsed. --> Try: {try_help}')

elif (sys.argv[2] != 'x' and sys.argv[2] != 'y' and sys.argv[2] != 'z' and sys.argv[2] != 'back'): 
   error(f'Polarization direction "{sys.argv[2]}" not supported.')

elif (len(sys.argv)==6 or len(sys.argv)==7):
   if (sys.argv[5]!='-norm') and (sys.argv[5]!='-sticks') and (sys.argv[5]!='-corr'): 
      error(f'Option "{sys.argv[5]}" not recognised.')
   elif (sys.argv[5]=='-norm'):
      normalize = True
   elif (sys.argv[5]=='-sticks'):
      sticks = True
   elif (sys.argv[5]=='-corr'):
      correct_ints = True

elif ((len(sys.argv)==6 and sys.argv[5]!='-corr') or
      (len(sys.argv)==7 and sys.argv[6]!='-corr')):
      print(sys.argv)
      if len(sys.argv)==6: error(f'Option "{sys.argv[5]}" not recognised.')
      if len(sys.argv)==7: error(f'Option "{sys.argv[6]}" not recognised.')

if ((len(sys.argv)==6 and sys.argv[5]=='-corr') or 
      (len(sys.argv)==7 and sys.argv[6]=='-corr')):
   correct_ints = True


pol = sys.argv[2] 
logfile = sys.argv[4]

check_file_exists(logfile)
# --------------------------------------------


# ---------------- Read ROA ------------------
freq_cm = []
roa_int = []

roa_found    = False
sticks_found = False

with open(logfile,'r') as f:
   for line in f:

      if (roa_found and sticks_found and len(line) == 1): break

      if (roa_found and sticks_found):
         freq_cm.append(float(line.split()[2]))
         if (pol=='x'): roa_int.append(float(line.split()[5]))
         if (pol=='y'): roa_int.append(float(line.split()[3]))
         if (pol=='back'): roa_int.append(float(line.split()[4]))
         if (pol=='z'): roa_int.append(float(line.split()[6]))

      if (line.startswith(roa_first_line)):          roa_found = True
      if ((roa_found) and line.startswith(' -')): sticks_found = True
# --------------------------------------------


# ----- Generate Spectrum, Plot, and Save ----
if (correct_ints):
# I_corr = I * ( wavenumber_campo_incidente - wavenumber_modo_normale )^4 / wavenumber_modo_normale
   for i in range(len(roa_int)):
      roa_int[i] = roa_int[i] * (incoming_field_ev*ev_to_wavenumbers-freq_cm[i])**4/freq_cm[i]

freqs = np.linspace(freqmin,freqmax,freqmax-freqmin)
roa_spec = np.zeros([freqmax-freqmin])

roa_spec = conv_stick(freqs,freq_cm,roa_int)

if (normalize):
   roa_spec_abs = [abs(x) for x in roa_spec]
   norm = max(roa_spec_abs)

   for i in range(freqmax-freqmin):
      roa_spec[i] = roa_spec[i]/norm 

# Create the plot
plt.figure(figsize=(10, 6))
plt.plot(freqs, roa_spec, linestyle='-')

# Reverse the x-axis
plt.gca().invert_xaxis()

# Set the labels
plt.xlabel('Wavenumber (cm$^{-1}$)')
plt.ylabel('I$_R$ - I$_L$ (a.u.)')
if (normalize): plt.ylabel('I$_R$ - I$_L$ (arb. units)')

# Set the title (optional)
plt.title(f'ROA Spectrum - {pol.upper()}')


plt.grid(True)

output_filename = f'ROA_spectrum_{pol}.png'
if (normalize): output_filename = f'ROA_spectrum_{pol}_NORM.png'

plt.savefig(output_filename, dpi=300, bbox_inches='tight')

plt.show()

output_csv = f'{logfile[:-4]}_ROA_{pol}.csv'
if (normalize): output_csv = f'{logfile[:-4]}_ROA_{pol}_NORM'
if (correct_ints): output_csv = output_csv + '_corrected'
output_csv = output_csv + '.csv' 
with open (output_csv, 'w') as f:
   for x,y in zip(freqs,roa_spec):
      f.write(f'{x:25.16f}   {y:25.16f}  \n')
# --------------------------------------------


# --------- Save single point values ---------
if (sticks):
   output_csv = f'{logfile[:-4]}_ROA_STICKS_{pol}.csv'
   with open (output_csv, 'w') as f:
      for x,y in zip(freq_cm,roa_int):
         f.write(f'{x:25.16f}   {y:25.16f}  \n')
# --------------------------------------------
