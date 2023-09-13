"""
File: dicom/data.py
"""

# Import packages and submodules

# Import classes and methods
from pybrors.dicom import DicomFile, DicomDir


class DicomData:
    """
    DICOM file class inheriting from GenericFile.

    Attributes
    ----------
    file_dir : str
        The directory containing the file.
    file_list : list[str]
        A list of file names in the directory.
    dataset : pydicom.dataset.FileDataset
        The DICOM dataset of the file.
    data : np.ndarray
        The DICOM data.
    """

    def __init__(self, file_path: str = None, dir_path: str = None) -> None:
        """
        Initializes a DICOM data object.

        Parameters
        ----------
        file_path : str
            The absolute path of the DICOM file.
        dir_path : str
            The absolute path of the DICOM directory.
        """

        # Load a single DICOM file
        if file_path is not None:
            self._get_file_data(file_path)

        # Load a DICOM serie
        elif dir_path is not None:
            self._get_dir_data(dir_path)

        else:
            err_msg = "No file or directory were provided to load Dicom data."
            raise FileNotFoundError(err_msg)

    def _get_file_data(self, file_path: str) -> None:
        """
        Load DICOM file from the given file path and extract its tags
        and data.

        Parameters
        ----------
        file_path : str
            The path to the DICOM file.
        """
        # Load DICOM file
        tmp_file = DicomFile(file_path=file_path)

        # Extract all DICOM tags
        self.dataset = tmp_file.dataset

        # Extract data from tags
        self.data = self.dataset.pixel_array

        # Extract file information
        self.file_dir   = tmp_file.file_dir
        self.file_list = [tmp_file.file_name]

    def _get_dir_data(self, dir_path: str) -> None:
        """
        Load DICOM directory and extract all DICOM tags.

        Parameters
        ----------
        dir_path : str
            The path to the directory containing the DICOM
            files.
        """
        # Load DICOM directory
        self.file_dir  = dir_path
        tmp_dir        = DicomDir(dir_path=self.file_dir)
        self.file_list = tmp_dir.file_list

        # Extract all DICOM tags
        tmp_data = []
        for tmp_file_path in tmp_dir.file_list:
            tmp_data = tmp_data.append(DicomData(file_path=tmp_file_path))
