# Import packages and submodules

# Import classes and methods
from pybrors.utils import GenericDir, GenericFile


def test_generic():
    """
    This function tests the GenericFile and GenericDir classes.

    It creates an instance of the GenericFile class with the file_path
    set to "ext/data/dicom/supported_file.dcm". It then prints out the
    properties of the GenericFile instance including file_path,
    file_dir, file_name, and file_ext.

    Next, it creates an instance of the GenericDir class with the
    dir_path set to "ext/data/dicom/dicom_exam". It then prints out the
    properties of the GenericDir instance including file_list.
    """    # Create file instance
    tmp = GenericFile(file_path="ext/data/dicom/supported_file.dcm")
    print(tmp)
    print(tmp.file_path)
    print(tmp.file_dir)
    print(tmp.file_name)
    print(tmp.file_ext)

    # Create directory instance
    tmp = GenericDir(dir_path="ext/data/dicom/dicom_exam")
    print(tmp)
    print(tmp.file_list)
