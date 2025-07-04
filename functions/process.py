import sys
import os
import numpy as np
import matplotlib.pyplot as plt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from classes import parameters
from matplotlib.ticker import ScalarFormatter

param = parameters.parameters()
# =====================================================================================
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
# =====================================================================================
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
        Plot and save the Raman spectrum as a PNG file.
    
        Args:
            freqs (numpy.ndarray): Array of frequency values for the spectrum.
            raman_spec (numpy.ndarray): Array of processed Raman intensities.
            normalize (bool): If True, use 'arb. units' for the y-label and save as *_NORM.png.
    
        Returns:
            None
        """
    
        plt.figure(figsize=(8, 6))
        plt.rcParams['font.family'] = 'Times New Roman'

        fontsize_label = 22
        fontsize_ticks = 20

        plt.plot(freqs, raman_spec, linestyle='-', color='blue')
        plt.xlabel('Wavenumber (cm$^{-1}$)', fontsize=fontsize_label, fontname='Times New Roman', labelpad=10)
        plt.ylabel('Raman Intensity (arb. units)' if normalize else 'Raman Intensity (a.u.)',
                   fontsize=fontsize_label, fontname='Times New Roman')
        plt.xticks(fontsize=fontsize_ticks, fontname='Times New Roman')
        plt.yticks(fontsize=fontsize_ticks, fontname='Times New Roman')
        plt.grid(False)

        # Add scientific notation offset (e.g., ×10¹⁵) to y-axis
        ax = plt.gca()
        formatter = ScalarFormatter(useMathText=True)
        formatter.set_powerlimits((0, 0))  # Always use scientific notation
        ax.yaxis.set_major_formatter(formatter)
        ax.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
        ax.yaxis.offsetText.set_fontsize(fontsize_ticks)
        ax.yaxis.offsetText.set_fontname('Times New Roman')

        plt.tight_layout()
        output_filename = 'RAMAN_spectrum_NORM.png' if normalize else 'RAMAN_spectrum.png'
        plt.savefig(output_filename, dpi=300, bbox_inches='tight')
        plt.show()
    # -------------------------------------------------------------------------------------
    # Read vibrational frequencies and intensities from the AMS file,
    # then generate, process, plot, and save the Raman spectrum.
    freq_cm, raman_int = read_raman_data(inp)
    freqs, raman_spec = generate_and_save_raman_spectrum(inp, freq_cm, raman_int)
    plot_raman_spectrum(freqs, raman_spec, normalize=inp.norm)
# =====================================================================================
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
        try:
            for ams_file in inp.ams_file:
               roa_found = False
               sticks_found = False
               with open(ams_file, 'r') as f:
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
        then saves the spectrum to a CSV file for each input AMS file.
    
        Args:
            inp: Input parameters object. Must have 'freq_min', 'freq_max', 'norm',
                 'incoming_field_ev', 'ev_to_wavenumbers', 'ams_file', and 'pol' attributes.
            freq_cm (list of float): Vibrational frequencies in cm^-1 (concatenated from all files).
            roa_int (list of float): ROA intensities (concatenated from all files).
    
        Returns:
            list: List of (freqs, roa_spec) tuples, one for each file.
        """
        n_files = len(inp.ams_file)
        roa_int_len = int(len(roa_int) / n_files)
        results = []
    
        # First, generate all spectra (before normalization) to find the global max if needed
        all_roa_specs = []
        all_freqs = []
        for n in range(n_files):
            freq_cm_slice = freq_cm[n * roa_int_len : (n + 1) * roa_int_len]
            roa_int_slice = roa_int[n * roa_int_len : (n + 1) * roa_int_len]
    
            # Apply intensity correction
            for i in range(len(roa_int_slice)):
                roa_int_slice[i] = roa_int_slice[i] * (inp.incoming_field_ev * param.ev_to_wavenumbers - freq_cm_slice[i])**4 / freq_cm_slice[i]
    
            n_points = int(inp.freq_max - inp.freq_min)
            freqs = np.linspace(inp.freq_min, inp.freq_max, n_points)
            roa_spec = conv_stick(freqs, freq_cm_slice, roa_int_slice)
    
            all_roa_specs.append(roa_spec)
            all_freqs.append(freqs)
    
        # Find the absolute maximum across all spectra for normalization
        if inp.norm:
            norm = np.max([np.max(np.abs(spec)) for spec in all_roa_specs])
        else:
            norm = 1.0
    
        for n in range(n_files):
            roa_spec = all_roa_specs[n]
            freqs = all_freqs[n]
    
            # Normalize with respect to the global maximum if requested
            if inp.norm and norm != 0:
                roa_spec = roa_spec / norm
    
            # Save the ROA spectrum to a CSV file
            ams_file = inp.ams_file[n]
            base = os.path.splitext(ams_file)[0]
            output_csv = f'{base}_ROA_{inp.pol}'
            if inp.norm:
                output_csv += '_NORM'
            output_csv += '.csv'
            with open(output_csv, 'w') as f:
                for x, y in zip(freqs, roa_spec):
                    f.write(f'{x:25.16f}   {y:25.16f}\n')
    
            results.append((freqs, roa_spec))
    
        return results
    # -------------------------------------------------------------------------------------
    def plot_roa_spectrum(results, pol, normalize=False):
        """
        Plot and save the ROA spectrum(s) as a PNG file.
    
        Args:
            results (list): List of (freqs, roa_spec) tuples, one for each file.
            pol (str): Polarization label (e.g., 'x', 'y', 'z', 'back').
            normalize (bool): If True, use 'arb. units' for the y-label and save as *_NORM.png.
    
        Returns:
            None
        """
    
        plt.figure(figsize=(8, 6))
        plt.rcParams['font.family'] = 'Times New Roman'

        fontsize_label = 22
        fontsize_ticks = 20
        
        colors = ['blue', 'red']
        labels = ['File 1', 'File 2']
    
        # Ensure results is always a list
        if isinstance(results, tuple):
            results = [results]
    
        plt.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)


        for idx, (freqs, roa_spec) in enumerate(results):
            color = colors[idx % len(colors)]
            label = labels[idx] if len(results) > 1 else None
            plt.plot(freqs, roa_spec, linestyle='-', color=color, label=label)
    
        # Set y-limits with margin
        all_y = np.concatenate([np.abs(roa_spec) for _, roa_spec in results])
        ymax = all_y.max()
        margin = 1.10
        plt.ylim(-ymax * margin, ymax * margin)

        ax = plt.gca()
        formatter = ScalarFormatter(useMathText=True)
        formatter.set_powerlimits((0, 0))  # Always use scientific notation
        ax.yaxis.set_major_formatter(formatter)
        ax.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
        
        # Make the offset text (e.g., ×10¹⁵) larger and in Times New Roman
        ax.yaxis.offsetText.set_fontsize(fontsize_ticks)
        ax.yaxis.offsetText.set_fontname('Times New Roman')
        #
        plt.xlabel('Wavenumber (cm$^{-1}$)', fontsize=fontsize_label, fontname='Times New Roman',labelpad=10)
        plt.ylabel('I$_R$ - I$_L$ (arb. units)' if normalize else 'I$_R$ - I$_L$ (a.u.)',
           fontsize=fontsize_label, fontname='Times New Roman')
        #plt.title(f'ROA Spectrum - {pol.upper()}', fontname='Times New Roman')
        plt.xticks(fontsize=fontsize_ticks, fontname='Times New Roman')
        plt.yticks(fontsize=fontsize_ticks, fontname='Times New Roman')
        plt.grid(False)
        #if len(results) > 1:
        #    plt.legend()
        plt.tight_layout()
        output_filename = f'ROA_spectrum_{pol}_NORM.png' if normalize else f'ROA_spectrum_{pol}.png'
        plt.savefig(output_filename, dpi=300, bbox_inches='tight')
        plt.show()
    # -------------------------------------------------------------------------------------
    # Read vibrational frequencies and intensities from the AMS file,
    # then generate, process, plot, and save the ROA spectrum.
    freq_cm, roa_int = read_roa_data(inp)
    results = generate_and_save_roa_spectrum(inp, freq_cm, roa_int)
    plot_roa_spectrum(results, inp.pol, normalize=inp.norm)

   
