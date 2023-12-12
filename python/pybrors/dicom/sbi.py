# File: dicom/sbi.py

# Import packages and submodules
import sys
import numpy

# Import classes and methods
from os.path import dirname, join, abspath
from ctypes import c_uint16, c_int32
from PIL import Image

# Import ext library
srtk_folder = abspath(join(dirname(__file__), "../../../ext/lib/Philips_SBI"))
sys.path.append(srtk_folder)
import SRTK
SRTK.SRTKRoot(srtk_folder)


# Import classes and methods
from .files import DicomFile


class SbiFile(DicomFile):

    def __init__(self, file_path: str = None) -> None:

        # Initialize parent attributes
        super().__init__(file_path)

        if self.dataset["ImageType"].value[2] != "SBI":
            raise ValueError("Not an SBI file.")

        if SRTK.Init(self.file_path) == 0:
            raise ValueError("SBI file could not be initialized.")

    def generate_monoe(self, energy: int = 70) -> numpy.ndarray:

        # allocate data for results
        msize = SRTK.GetMatrixSize ()
        dsize = msize * msize
        data = (c_uint16 * dsize)()

        par = (c_int32 * 1) ()
        par[0] = energy

        if SRTK.CalculateResult ("MonoE", data, par) == 1:
            return numpy.reshape(data, (msize, msize))

        else:
            raise ValueError("MonoE image could not be generated.")
