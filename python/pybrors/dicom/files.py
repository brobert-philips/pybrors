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
import pandas
import pydicom

# Import classes and methods
from pybrors.utils import GenericFile, GenericDir


TAGS_CLEARED = [
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
    "ImplementationVersionName",
    "ProcedureCodeSequence",
    "PerformedProcedureStepDescription",
    "PerformedProtocolCodeSequence",
    "RetrieveAETitle",
    "ReferencedPerformedProcedureStepSequence",
]
"""Constant containing all cleared DICOM tags."""

TAGS_DATAFRAME = [
    "ImageType",
    "InstanceCreationDate",
    "StudyDate",
    "SeriesDate",
    "AcquisitionDate",
    "ContentDate",
    "AccessionNumber",
    "Modality",
    "StationName",
    "PatientName",
    "PatientID",
    "PatientBirthDate",
    "SeriesInstanceUID",
    "StudyID",
    "InstanceNumber",
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
            new_path += f"{os.sep}{self._build_anonymized_filepath(anonym_dataset)}"

        # Control if path is accessible and create subdirectories if needed
        if not os.path.exists(os.path.dirname(new_path)):
            os.makedirs(os.path.dirname(new_path))

        # Save anonymized file
        anonym_dataset.save_as(new_path)
        return True


    def _build_anonymized_filepath(self, dataset: pydicom.dataset.Dataset) -> str:
        """
        Builds an anonymized file path based on the given dataset.

        Parameters
        ----------
        dataset : pydicom.dataset.Dataset
            The dataset containing the DICOM tags.

        Returns
        -------
        str
            The absolute file path of the anonymized file.
        """
        # Extract DICOM tags
        pid        = dataset["PatientID"].value
        series_uid = dataset["SeriesInstanceUID"].value
        modality   = dataset["Modality"].value

        # Extract ImageType
        if "ImageType" in dataset:
            img_type = dataset["ImageType"].value
            img_type = img_type[2] if len(img_type) > 2 else "UNK"
        else:
            print("ImageType set to 'UNK'.")
            img_type = "UNK"

        # Extract InstanceNumber
        if "InstanceNumber" in dataset:
            inst_num = dataset["InstanceNumber"].value
        else:
            print("InstanceNumber set to '00000'.")
            inst_num = "00000"

        # Extract AccessionNumber
        if "AccessionNumber" in dataset:
            acc_num = dataset["AccessionNumber"].value
        else:
            print("AccessionNumber set to '12345'.")
            acc_num = "12345"

        # Create new file absolute path
        new_path  = f"{pid}{os.sep}{acc_num[-16:]}{os.sep}"
        new_path += f"{series_uid[-16:]}_{modality}{os.sep}"
        new_path += f"{img_type}_{inst_num:05}.dcm"

        return new_path


    def get_dicom_info(self) -> dict:
        """
        Generate a dictionary containing DICOM information.

        This function iterates through the TAGS_DATAFRAME list and
        checks if each tag is present in the dataset. If the tag is
        present, the corresponding value is added to the dictionary. If
        the tag is not present, the value "UNK" is added to the
        dictionary.

        Returns
        -------
        dict
            A dictionary containing DICOM information.
        """
        dicom_info = {}
        for tag in TAGS_DATAFRAME:
            if tag in self.dataset:
                dicom_info[tag] = self.dataset[tag].value
            else:
                dicom_info[tag] = "UNK"

        return dicom_info

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
        study_date   = dataset["StudyDate"].value
        study_time   = dataset["StudyTime"].value
        study_uid    = dataset["StudyInstanceUID"].value

        # Get DeviceSerialNumber
        if "DeviceSerialNumber" not in dataset:
            print(self.file_path)
            print(f"Set DeviceSerialNumber to {datetime.today().strftime('%Y%m%d')}.")
            dataset.DeviceSerialNumber = datetime.today().strftime("%Y%m%d")
        serial_num = dataset["DeviceSerialNumber"].value

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
        for tag in TAGS_CLEARED:
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

        # Delete all anonymized files and remove them from files list
        anonymized_files = [file for file in self.file_list if "anonymized" in file]
        self.file_list   = [file for file in self.file_list if "anonymized" not in file]
        for file in anonymized_files:
            os.remove(file)

        # Build files DataFrame
        self.dicom_df = pandas.DataFrame(columns=TAGS_DATAFRAME)
        for file in self.file_list:
            try:
                dicom_file = DicomFile(file)
                dicom_info = dicom_file.get_dicom_info()
                dicom_info["path"] = file
                self.dicom_df = pandas.concat(
                    [self.dicom_df, pandas.DataFrame([dicom_info])],
                    ignore_index=True
                )
            except FileNotFoundError:
                print("File %s does not exist.", file)

        # Extract list of not supported files
        non_dicom_files = self.file_list
        self.file_list  = list(self.dicom_df.path)
        non_dicom_files = list(set(non_dicom_files) - set(self.file_list))

    def anonymize(self) -> bool:
        """
        Anonymizes the DICOM files in the specified directory.

        Returns
        -------
        bool
            True if the anonymization is successful, False otherwise.
        """
        # Check if new directory path is given
        new_path = os.path.join(self.dir_path, "anonymized")

        # Control if path is accessible and create subdirectories if needed
        if not os.path.exists(new_path):
            os.makedirs(new_path)

        # Anonymize DICOM files
        for file_path in self.file_list:
            dicom_file = DicomFile(file_path)
            if not dicom_file.anonymize(new_dir_path=new_path):
                return False
        print("Anonymized %i DICOM files.", len(self.file_list))
        return True
