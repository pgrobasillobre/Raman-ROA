class input_class:
   """
   Manages user-defined parameters for Raman/ROA data extraction
   """

   def __init__(self):
      """
      Initializes input parameters for Raman/ROA data extraction.
      """

      # -- Raman or ROA?
      self.raman = False
      self.roa = False

      # -- Frequency range
      self.freq_min = 0.0
      self.freq_max = 0.0

      # -- AMS file
      self.ams_file = ""

      # -- Other options
      self.norm = False # Normalize the data
      
