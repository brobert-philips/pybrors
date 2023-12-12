# File: dicom/sbi.py
# TODO: create a plugin localization and validation

# Import packages and submodules
import sys

# Import classes and methods
from os.path import dirname, join, abspath
from ctypes import c_uint16, c_int32
from scipy.optimize import curve_fit

# Import packages and submodules
import numpy

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

        # Allocate data for results
        msize = SRTK.GetMatrixSize ()
        dsize = msize * msize
        data = (c_uint16 * dsize)()

        par = (c_int32 * 1) ()
        par[0] = energy

        if SRTK.CalculateResult ("MonoE", data, par) == 1:
            return numpy.reshape(data, (msize, msize))

        else:
            raise ValueError("MonoE image could not be generated.")

    def generate_exponential(self) -> numpy.ndarray:

        # Generate MonoE maps form 40 keV to 190 keV
        energy_range = numpy.arange(40, 200, 10)
        monoe_stack = [self.generate_monoe(energy) for energy in energy_range]
        monoe_stack = numpy.stack(monoe_stack, axis=2)

        # Define exponential model
        def exponential_model(E, mu_0, mu_inf, E_C):
            return (mu_0 - mu_inf) * numpy.exp(-E / E_C) + mu_inf

        # Exponential fit voxel by voxel
        exponential_map = numpy.zeros([monoe_stack.shape[0], monoe_stack.shape[1], 3])
        std_threshold = numpy.max(monoe_stack) * 0.01
        for i in range(monoe_stack.shape[0]):
            for j in range(monoe_stack.shape[1]):
                tmp_std = numpy.std(monoe_stack[i,j,:])
                if tmp_std > std_threshold:
                    exponential_map[i,j,:], _ = curve_fit(
                        exponential_model,
                        energy_range,
                        monoe_stack[i,j,:]
                    )
                else:
                    tmp_mu = numpy.mean(monoe_stack[i,j,:])
                    exponential_map[i,j,:] = [tmp_mu, tmp_mu, 0]

        return exponential_map
