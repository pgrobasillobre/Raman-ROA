class input_class:
   """
   Stores and manages user-defined parameters for Raman/ROA data extraction.
   """

   def __init__(self):
      """
      Initializes all input parameters for Raman/ROA data extraction to their default values.
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
      self.pol = ""
      self.incoming_field_ev = 0.0


      
