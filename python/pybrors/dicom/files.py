"""
File: dicom/files.py
"""

# Import packages and submodules
import copy
import os
import platform
import re

# Import classes and methods
from datetime import datetime

# Import packages and submodules
import pydicom

# Import classes and methods
from pybrors.utils import GenericFile, GenericDir




CLEAR_TAGS = [
    "InstitutionName",
    "InstitutionAddress",
    "ReferringPhysicianName",
    "ReferringPhysicianAddress",
    "ReferringPhysicianTelephoneNumbers",
    "InstitutionalDepartmentName",
    "PhysiciansOfRecord",
    "PerformingPhysicianName",
    "NameOfPhysiciansReadingStudy",
    "OperatorsName",
    "AdmittingDiagnosesDescription",
    "OtherPatientIDs",
    "OtherPatientNames",
    "MedicalRecordLocator",
    "EthnicGroup",
    "Occupation",
    "AdditionalPatientHistory",
    "PatientComments",
    "RequestingPhysician",
    "RequestingService",
    "RequestedProcedureDescription",
    "ScheduledPerformingPhysicianName",
    "PerformedStationAETitle",
    "RequestAttributesSequence",
    "RequestedProcedureID",
    "IssueDateOfImagingServiceRequest",
    "ContentSequence",
]
"""Constant containing all cleared DICOM tags."""


class DicomFile(GenericFile):
    """
    DICOM file class inheriting from GenericFile.

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

    FILE_TYPES = {
        ""    : "All files"  ,
        ".dcm": "DICOM files",
    }
    """Supported file extensions."""


    def __init__(self, file_path: str = None) -> None:
        """
        Initializes a DICOM file object.

        Parameters
        ----------
        file_path : str
            The absolute path of the DICOM file. If not provided, a
            file selection dialog will be displayed.

        Raises
        ------
        FileNotFoundError
            If the file path is invalid or the file is not supported.
        """        # Select file if not provided
        # Initialize parent attributes
        super().__init__(file_path)

        # Retrieve DICOM dataset
        self.dataset = pydicom.dcmread(self.file_path)


    @staticmethod
    def test_file(file_path: str = None) -> bool:
        """
        Test if file exists, is writable and is a DICOM supported file.

        Parameters
        ----------
        file_path : str
            Path to the file.

        Returns
        -------
        bool
            True if file exists and is writable, False otherwise.
        """
        # Test if file exists and is writable
        if not GenericFile.test_file(file_path):
            return False
        try:
            dicom_tags = pydicom.dcmread(file_path)
        except pydicom.errors.InvalidDicomError:
            print("No DICOM file found (%s).", file_path)
            return False

        # Modality tag must exist
        if "Modality" not in dicom_tags:
            print("No ImageType tag.")
            return False

        return True


    def anonymize(self, new_dir_path: str = None) -> bool:
        """
        Anonymize a DICOM file.

        This method applies the `_anonymize_dataset` private method to
        the DICOM file dataset.

        If `new_dir_path` is given, the anonymized file is saved in the
        `new_dir_path` directory according to the following convention:
        * subdirectory is [PID]/[STUDY_UID]/[SERIES_UID]_[MODALITY]
        * file name is [IMG_TYPE]_[IMG_NUM].dcm

        If `new_dir_path` is not given, the anonymized file is saved
        in the same directory with `_anonymized.dcm` suffix.

        Parameters
        ----------
        new_dir_path : str
            Absolute path to the new anonymized DICOM file/directory.
        """
        # Check if new directory path is given
        if new_dir_path is None:
            new_path  = self.file_dir + os.sep
            new_path += self.file_name[:-len(self.file_ext)] + "_anonymized.dcm"
        else:
            if GenericDir.test_dir(new_dir_path):
                new_path = new_dir_path
                new_path = os.path.join(new_path, "anonymized")
            else:
                print("Directory %s does not exist.", new_dir_path)
                return False
        new_path = os.path.abspath(new_path)

        # Anonymize DICOM dataset
        anonym_status, anonym_dataset = self._anonymize_dataset()
        if not anonym_status:
            print("Dataset could not be anonymized.")
            return False

        # Build anonymized file name if new_path is a directory
        if GenericDir.test_dir(new_path):
            # Extract DICOM tags
            pid        = anonym_dataset["PatientID"].value
            acc_num    = anonym_dataset["AccessionNumber"].value
            series_uid = anonym_dataset["SeriesInstanceUID"].value
            modality   = anonym_dataset["Modality"].value
            inst_num   = anonym_dataset["InstanceNumber"].value

            # Extract ImageType
            if "ImageType" in anonym_dataset:
                img_type = anonym_dataset["ImageType"].value
                img_type = img_type[2] if len(img_type) > 2 else "UNK"
            else:
                img_type = "UNK"

            # Create new file absolute path
            new_path += f"{os.sep}{pid}{os.sep}{acc_num[-16:]}{os.sep}"
            new_path += f"{series_uid[-16:]}_{modality}{os.sep}"
            new_path += f"  {img_type}_{inst_num:05}.dcm"

        # Control if path is accessible and create subdirectories if needed
        if not os.path.exists(os.path.dirname(new_path)):
            os.makedirs(os.path.dirname(new_path))

        # Save anonymized file
        anonym_dataset.save_as(new_path)
        return True


    def _anonymize_dataset(self) -> (bool, pydicom.dataset.FileDataset):
        """
        Anonymize DICOM dataset.

        Returns
        -------
        bool
            True if anonymized, False otherwise.
        pydicom.Dataset
            Anonymized DICOM dataset.
        """
        # Retrieve DICOM tags
        dataset      = copy.deepcopy(self.dataset)
        serial_num   = dataset["DeviceSerialNumber"].value
        study_date   = dataset["StudyDate"].value
        study_time   = dataset["StudyTime"].value
        study_uid    = dataset["StudyInstanceUID"].value

        # Reformat study_uid
        study_uid = study_uid.replace(".","+")
        study_uid = sum(map(int, re.findall(r'[+-]?\d+', study_uid)))
        study_uid = str(hex(int(study_uid))).upper()[2:]

        # Control and reformat values
        if not serial_num.isnumeric():
            serial_num = datetime.today().strftime("%y%m%d")

        # Create new values
        new_pid        = serial_num + study_date[2:] + study_time[:4]
        new_pid        = str(hex(int(new_pid))).upper()[2:]
        new_study_date = study_date[:-4] + "0101"
        new_birth_date = dataset["PatientBirthDate"].value
        new_birth_date = new_birth_date[:-4] + "0101"
        new_station    = platform.node().upper()

        # Anonymize tags
        tags = [
            "StationName",
            "InstanceCreationDate",
            "StudyDate",
            "SeriesDate",
            "AcquisitionDate",
            "ContentDate",
            "AccessionNumber",
            "PatientName",
            "PatientID",
            "PatientBirthDate",
            "StudyID",
        ]
        values = [
            new_station   , new_study_date, new_study_date  , new_study_date,
            new_study_date, new_study_date, study_uid [-16:], new_pid       ,
            new_pid       , new_birth_date, study_uid[-16:] ,
        ]
        for tag, value in zip(tags, values):
            # Check if tag exists in DICOM dataset
            if tag in dataset:
                print("Set tag %s to %s.", tag, value)
                dataset[tag].value = value
            else:
                print("DICOM dataset has no %s tag.", tag)

        # Delete tags
        for tag in CLEAR_TAGS:
            # Check if tag exists in DICOM dataset
            if tag in dataset:
                print("Clear tag %s.", tag)
                dataset[tag].clear()

            else:
                print("DICOM dataset has no %s tag.", tag)

        return True, dataset




class DicomDir(GenericDir):
    """
    DICOM directory class inheriting from GenericDir.

    Attributes
    ----------
    dir_path : str
        The path of the directory.
    file_list : list[str]
        A list of file paths in the directory.
    """

    def __init__(self, dir_path: str = None) -> None:
        """
        Initialize a DICOM directory object.

        This method first initializes the GenericDir attributes. It
        builds a DICOM database for all supported DICOM files.

        Parameters
        ----------
        dir_path : str
            Path to the directory.
        """
        # Initialize parent attributes
        super().__init__(dir_path, DicomFile)
