class parameters:
    """
    Manages user-defined parameters for Raman/ROA data extraction
    """

    def __init__(self):
        """
        Initializes input parameters for Raman/ROA data extraction.
        """

        self.fwhm    = 20.0 # cm^{-1} Taken from: https://doi.org/10.1021/jp502107f
        self.ev_to_wavenumbers = 8065.54429 # cm^{-1}

        self.raman_first_line = ' Frequency (New) [cm-1] | Raman Int. [A^4/amu]'
        self.roa_first_line = ' Frequency (New) [cm-1] |      Delta(0)'

