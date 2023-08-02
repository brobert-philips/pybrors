"""
File: tests/test_dicom.py
"""

# Import packages and submodules

# Import classes and methods
from pybrors.utils import GenericDir, GenericFile
from pybrors.dicom import DicomFile, DicomDir


def test_generic():
    """
    A function to test the GenericFile and GenericDir classes.

    This function creates an instance of the GenericFile class with the
    file_path parameter set to "ext/data/dicom/dicom_img_file.dcm". It
    then prints out the instance, as well as the values of its
    file_path, file_dir, file_name, and file_ext attributes.

    Next, the function creates an instance of the GenericDir class with
    the dir_path parameter set to "ext/data/dicom/dicom_exam". It
    then prints out the instance, as well as the value of its file_list
    attribute.

    There is no return value for this function.
    """
    tmp = GenericFile(file_path="ext/data/dicom/dicom_img_file.dcm")
    print(tmp)
    print(tmp.file_path)
    print(tmp.file_dir)
    print(tmp.file_name)
    print(tmp.file_ext)

    # Create directory instance
    tmp = GenericDir(dir_path="ext/data/dicom/dicom_exam")
    print(tmp)
    print(tmp.file_list)


def test_dicom_file():
    """
    Test the functionality of the DicomFile class.

    This function creates an instance of the DicomFile class using a
    specified file path. It then prints the instance and the value of
    the "Modality" attribute of its dataset.

    Next, it checks if the DICOM file can be anonymized using the
    anonymize() method of the DicomFile class. If the anonymization is
    successful, it prints "DICOM has been anonymized." Otherwise, it
    prints "DICOM has not been anonymized."

    Finally, it prints the instance again and the value of the
    "PatientName" attribute of its dataset.
    """
    # Create file instance
    tmp = DicomFile(file_path="ext/data/dicom/dicom_img_file.dcm")
    print(tmp)
    print(tmp.dataset["Modality"].value)

    # Anonymize DICOM file
    if tmp.anonymize():
        print("DICOM has been anonymized.")
    else:
        print("DICOM has not been anonymized.")

    print(tmp)
    print(tmp.dataset["PatientName"])
