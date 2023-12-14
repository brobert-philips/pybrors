# File: dicom/sbi.py
# TODO: create a plugin localization and validation
# TODO: create a save exponential maps

# Import packages and submodules
import sys

# Import classes and methods
from os.path import dirname, join, abspath
from ctypes import c_uint16, c_int32
from scipy.optimize import curve_fit
from copy import deepcopy

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
    """
    A class representing an SBI file.

    Inherits from the DicomFile class.

    Attributes
    ----------
    FILE_TYPES : dict[str, str]
        The supported file extensions and their descriptions.
    file_path : str
        The absolute path of the file.
    file_name : str
        The name of the file.
    file_ext : str
        The extension of the file.
    file_dir : str
        The directory containing the file.
    dataset : pydicom.dataset.FileDataset
        The DICOM dataset of the file.
    """

    def __init__(self, file_path: str = None) -> None:
        """
        Initializes the object.

        Parameters
        ----------
        file_path : str
            The path to the file. Defaults to None.

        Raises
        ------
        ValueError
            If the file is not an SBI file or if the SBI file could not be
            initialized.

        Returns:
            None
        """

        # Initialize parent attributes
        super().__init__(file_path)

        if self.dataset["ImageType"].value[2] != "SBI":
            raise ValueError("Not an SBI file.")

        if SRTK.Init(self.file_path) == 0:
            raise ValueError("SBI file could not be initialized.")

    def generate_monoe(self, energy: int = 70) -> numpy.ndarray:
        """
        Generate a MonoE image using the given energy value.

        Parameters
        ----------
        energy : int
            The energy value for the MonoE image. Defaults to 70.

        Returns
        -------
        numpy.ndarray
            The MonoE image as a numpy array.

        Raises
        ------
        ValueError
            If the MonoE image could not be generated.
        """

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
        """
        Generate an exponential map using MonoE maps from 40 keV to 190
        keV.

        Returns
    	-------
    	numpy.ndarray
    	    The exponential map with shape [num_rows, num_columns, 3].
    	"""

        # Generate MonoE maps form 40 keV to 190 keV
        energy_range = numpy.arange(40, 200, 10)
        monoe_stack = [self.generate_monoe(energy) for energy in energy_range]
        monoe_stack = numpy.stack(monoe_stack, axis=2)

        # Define exponential model
        def exponential_model(energy, mu_0, mu_inf, e_c):
            return (mu_0 - mu_inf) * numpy.exp(-energy / e_c) + mu_inf

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

    def export_exp_maps(self) -> None:
        """
        Export the exponential maps.
        """

        # Generate exponential maps and rescale values
        rescale_slope = self.dataset.RescaleSlope
        rescale_intercept = self.dataset.RescaleIntercept
        exp_maps = (self.generate_exponential() - rescale_intercept) / rescale_slope
        ext = self.file_ext

        # Copy DICOM dataset to export mu_0 map
        mu_0 = deepcopy(self.dataset)
        mu_0["ImageType"].value[2] = "MU0"
        mu_0.Rows = exp_maps.shape[0]
        mu_0.Columns = exp_maps.shape[1]
        mu_0.PixelData = exp_maps[:,:,0].astype(numpy.float16).tobytes()
        new_path = self.file_path.replace(ext, f"_mu0{ext}")
        mu_0.save_as(new_path)

        # Copy DICOM dataset to export mu_inf map
        mu_inf = deepcopy(self.dataset)
        mu_inf["ImageType"].value[2] = "MUINF"
        mu_inf.Rows = exp_maps.shape[0]
        mu_inf.Columns = exp_maps.shape[1]
        mu_inf.PixelData = exp_maps[:,:,1].astype(numpy.float16).tobytes()
        new_path = self.file_path.replace(ext, f"_muinf{ext}")
        mu_inf.save_as(new_path)

        # Copy DICOM dataset to export e_c map

        e_c = deepcopy(self.dataset)
        e_c["ImageType"].value[2] = "EC"
        e_c.Rows = exp_maps.shape[0]
        e_c.Columns = exp_maps.shape[1]
        e_c.PixelData = (10*exp_maps[:,:,2]).astype(numpy.float16).tobytes()
        new_path = self.file_path.replace(ext, f"_ec{ext}")
        e_c.save_as(new_path)
