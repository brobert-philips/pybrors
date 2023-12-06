# File: dicom/sbi.py

# Import packages and submodules

# Import classes and methods
from .files import DicomFile

class SbiFile(DicomFile):

    def __init__(self, file_path: str = None) -> None:

        # Initialize parent attributes
        super().__init__(file_path)

        if self.dataset["ImageType"].value[2] != "SBI":
            raise ValueError("Not an SBI file.")
