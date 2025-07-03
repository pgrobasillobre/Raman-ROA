import sys
import os
import numpy as np
import matplotlib.pyplot as plt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from classes import parameters

param = parameters.parameters()
# -------------------------------------------------------------------------------------
def conv_stick(freqs, freq_peaks, int_peaks):
    """
    Convolves stick spectrum with a Lorentzian broadening.

    Args:
        freqs (numpy.ndarray): Array of frequency values for the spectrum.
        freq_peaks (list of float): Peak positions (frequencies) in cm^-1.
        int_peaks (list of float): Intensities at each peak.

    Returns:
        numpy.ndarray: Broadened spectrum.
    """
    spectrum = np.zeros(np.shape(freqs))
    for peak in range(len(freq_peaks)):
        spectrum += (param.fwhm / ((freqs - freq_peaks[peak])**2 + param.fwhm)) * int_peaks[peak]
    return spectrum
# -------------------------------------------------------------------------------------
def raman(inp):
    """
    Extraction of Raman data and processing.
    
    Args:
        inp (input_class): Input parameters for Raman data extraction.
    
    Returns:
        None: This function does not return any value
    """
    # -------------------------------------------------------------------------------------
    def read_raman_data(inp):
        """
        Reads Raman data from the specified AMS file.

        Args:
            inp: Input parameters object. 

        Returns:
            tuple: Two lists:
                - freq_cm (list of float): Vibrational frequencies in cm^-1.
                - raman_int (list of float): Corresponding Raman intensities.
        """
        freq_cm = []
        raman_int = []
        raman_found = False
        sticks_found = False
        try:
            with open(inp.ams_file, 'r') as f:
                for line in f:
                    if raman_found and sticks_found and len(line.strip()) == 0:
                        break
                    if raman_found and sticks_found:
                        parts = line.split()
                        if len(parts) > 3:
                            freq_cm.append(float(parts[2]))
                            raman_int.append(float(parts[3]))
                    if line.startswith(param.raman_first_line):
                        raman_found = True
                    if raman_found and line.startswith(' -'):
                        sticks_found = True

        except Exception as e:
            print(f"Error reading Raman data: {e}")

        return freq_cm, raman_int
    # -------------------------------------------------------------------------------------
    def generate_and_save_raman_spectrum(inp, freq_cm, raman_int):
        """
        Generates the Raman spectrum by applying intensity correction and optional normalization,
        then saves the spectrum to a CSV file.
    
        Args:
            inp: Input parameters object. Must have 'freq_min', 'freq_max', 'norm', 
                 'incoming_field_ev', and 'ev_to_wavenumbers' attributes.
            freq_cm (list of float): Vibrational frequencies in cm^-1.
            raman_int (list of float): Raman intensities.
    
        Returns:
            tuple:
                freqs (numpy.ndarray): Array of frequency values for the spectrum.
                raman_spec (numpy.ndarray): Array of processed Raman intensities.
        """
        # Apply intensity correction
        # I_corr = I * ( wavenumber_inc_efield - wavenumber_normalmode )^4 / wavenumber_normalmode
        for i in range(len(raman_int)):
            raman_int[i] = raman_int[i] * (inp.incoming_field_ev * param.ev_to_wavenumbers - freq_cm[i])**4 / freq_cm[i]
    
        # Generate the Raman spectrum from a Lorentzian convolution
        n_points = int(inp.freq_max - inp.freq_min)
        freqs = np.linspace(inp.freq_min, inp.freq_max, n_points)
        raman_spec = conv_stick(freqs, freq_cm, raman_int)
    
        # Normalize the Raman spectrum if requested
        if inp.norm:
            raman_spec_abs = np.abs(raman_spec)
            norm = np.max(raman_spec_abs)
            if norm != 0:
                raman_spec = raman_spec / norm

        # Save the Raman spectrum to a CSV file
        output_csv = f'{inp.ams_file[:-4]}_RAMAN.csv'
        if inp.norm: output_csv = f'{inp.ams_file[:-4]}_RAMAN_NORM.csv'
        with open(output_csv, 'w') as f:
            for x, y in zip(freqs, raman_spec):
                f.write(f'{x:25.16f}   {y:25.16f}\n')    

        return freqs, raman_spec
    # -------------------------------------------------------------------------------------
    def plot_raman_spectrum(freqs, raman_spec, normalize=False):
        """
        Plots and saves the Raman spectrum as a PNG file.
    
        Args:
            freqs (numpy.ndarray): Array of frequency values for the spectrum.
            raman_spec (numpy.ndarray): Array of processed Raman intensities.
            normalize (bool): If True, use 'arb. units' for the y-label and save as *_NORM.png.
    
        Returns:
            None
        """
        import matplotlib.pyplot as plt
    
        plt.figure(figsize=(10, 6))
        plt.plot(freqs, raman_spec, linestyle='-')
        plt.gca().invert_xaxis()
        plt.xlabel('Wavenumber (cm$^{-1}$)')
        plt.ylabel('Raman Intensity (arb. units)' if normalize else 'Raman Intensity (a.u.)')
        plt.grid(True)
    
        output_filename = 'RAMAN_spectrum_NORM.png' if normalize else 'RAMAN_spectrum.png'
        plt.savefig(output_filename, dpi=300, bbox_inches='tight')
        plt.show()
    # -------------------------------------------------------------------------------------
    # Read vibrational frequencies and intensities from the AMS file,
    # then generate, process, plot, and save the Raman spectrum.
    freq_cm, raman_int = read_raman_data(inp)
    freqs, raman_spec = generate_and_save_raman_spectrum(inp, freq_cm, raman_int)
    plot_raman_spectrum(freqs, raman_spec, normalize=inp.norm)
# -------------------------------------------------------------------------------------
def roa(inp):
    """
    Extraction of ROA data and processing.
    
    Args:
        inp (input_class): Input parameters for Raman data extraction.
    
    Returns:
        None: This function does not return any value
    """
    # -------------------------------------------------------------------------------------
    def read_roa_data(inp):
        """
        Reads ROA data from the specified AMS file, extracting intensities based on polarization.
    
        Args:
            inp: Input parameters object. 
    
        Returns:
            tuple:
                freq_cm (list of float): Vibrational frequencies in cm^-1.
                roa_int (list of float): Corresponding ROA intensities for the selected polarization.
        """
        freq_cm = []
        roa_int = []
        roa_found = False
        sticks_found = False
        try:
            with open(inp.ams_file, 'r') as f:
                for line in f:
                    if roa_found and sticks_found and len(line.strip()) == 0:
                        break
                    if roa_found and sticks_found:
                        parts = line.split()
                        if len(parts) > 6:
                            freq_cm.append(float(parts[2]))
                            if inp.pol == 'x':
                                roa_int.append(float(parts[5]))
                            elif inp.pol == 'y':
                                roa_int.append(float(parts[3]))
                            elif inp.pol == 'back':
                                roa_int.append(float(parts[4]))
                            elif inp.pol == 'z':
                                roa_int.append(float(parts[6]))
                    if line.startswith(param.roa_first_line):
                        roa_found = True
                    if roa_found and line.startswith(' -'):
                        sticks_found = True

        except Exception as e:
            print(f"Error reading ROA data: {e}")

        return freq_cm, roa_int
    # -------------------------------------------------------------------------------------
    def generate_and_save_roa_spectrum(inp, freq_cm, roa_int):
        """
        Generates the ROA spectrum by applying intensity correction and optional normalization,
        then saves the spectrum to a CSV file.
    
        Args:
            inp: Input parameters object. Must have 'freq_min', 'freq_max', 'norm',
                 'incoming_field_ev', 'ev_to_wavenumbers', 'ams_file', and 'pol' attributes.
            freq_cm (list of float): Vibrational frequencies in cm^-1.
            roa_int (list of float): ROA intensities.
    
        Returns:
            tuple:
                freqs (numpy.ndarray): Array of frequency values for the spectrum.
                roa_spec (numpy.ndarray): Array of processed ROA intensities.
        """
        # Apply intensity correction
        # I_corr = I * ( wavenumber_inc_efield - wavenumber_normalmode )^4 / wavenumber_normalmode
        for i in range(len(roa_int)):
            roa_int[i] = roa_int[i] * (inp.incoming_field_ev * param.ev_to_wavenumbers - freq_cm[i])**4 / freq_cm[i]
    
        n_points = int(inp.freq_max - inp.freq_min)
        freqs = np.linspace(inp.freq_min, inp.freq_max, n_points)
        roa_spec = conv_stick(freqs, freq_cm, roa_int)
    
        # Normalize the ROA spectrum if requested
        if inp.norm:
            roa_spec_abs = np.abs(roa_spec)
            norm = np.max(roa_spec_abs)
            if norm != 0:
                roa_spec = roa_spec / norm
    
        # Save the ROA spectrum to a CSV file
        output_csv = f'{inp.ams_file[:-4]}_ROA_{inp.pol}.csv'
        if inp.norm:
            output_csv = f'{inp.ams_file[:-4]}_ROA_{inp.pol}_NORM.csv'
        with open(output_csv, 'w') as f:
            for x, y in zip(freqs, roa_spec):
                f.write(f'{x:25.16f}   {y:25.16f}\n')
    
        return freqs, roa_spec
    # -------------------------------------------------------------------------------------
    # Read vibrational frequencies and intensities from the AMS file,
    # then generate, process, plot, and save the ROA spectrum.
    freq_cm, raman_int = read_roa_data(inp)
    freqs, raman_spec = generate_and_save_roa_spectrum(inp, freq_cm, raman_int)
    #plot_raman_spectrum(freqs, raman_spec, normalize=inp.norm)


   
