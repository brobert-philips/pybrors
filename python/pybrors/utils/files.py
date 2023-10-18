"""
File: utils/files.py
"""

# Import packages and submodules
import os

# Import classes and methods
from PyQt6.QtWidgets import QApplication, QFileDialog




class GenericFile:
    """
    Represents a generic file.

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
    """

    FILE_TYPES = {
        "*": "All files",
    }
    """Supported file extensions."""


    def __init__(self, file_path: str = None) -> None:
        """
        Initializes a GenericFile object.

        Parameters
        ----------
        file_path : str
            The absolute path of the file. If not provided, a file
            selection dialog will be displayed.

        Raises
        ------
        FileNotFoundError
            If the file path is invalid or the file is not supported.
        """        # Select file if not provided
        if file_path is None:
            # Build file types dict
            file_types = \
                [f"{value} (*.{key})" for key, value in self.FILE_TYPES.items()]
            file_types = ";;".join(file_types)

            # Select file dialog
            file_path = GenericFile.dialog_select_file(opt=file_types)

        # Generate absolute file and control if file is supported
        self.file_path = os.path.abspath(file_path)
        if not self.__class__.test_file(self.file_path):
            err_msg = f"File is not supported ({self.file_path})."
            # logger.error(err_msg)
            raise FileNotFoundError(err_msg)

        # Extract file information
        self.file_name = os.path.basename(self.file_path)
        self.file_ext  = os.path.splitext(self.file_name)[1]
        self.file_dir  = os.path.dirname (self.file_path)


    def __str__(self) -> str:
        """
        Convert the object to a string representation.

        Returns
        -------
            str: The string representation of the object.
        """
        # Build the string
        class_name  = self.__class__.__name__
        return_str  = f"{class_name}(file_name: {self.file_name}"
        return_str += f" ; file_dir: {self.file_dir})"

        # Return the string
        return return_str


    def __eq__(self, __value: object) -> bool:
        """
        Check if the current object is equal to the given object based
        on their file paths.

        Parameters
        ----------
        __value : object
            The object to compare with.

        Returns
        -------
        bool
            True if the file paths are equal, False otherwise.
        """
        return self.file_path == __value.file_path


    @staticmethod
    def test_file(file_path: str = None) -> bool:
        """
        Check if a file exists and if it is readable and writable.

        Parameters
        ----------
        file_path : str
            The path to the file to be checked.

        Returns
        -------
        bool
            True if the file exists and is readable and writable,
            False otherwise.
        """
        # Check file path and reformat it
        if file_path is None:
            err_msg = "No file path was provided."
            # logger.error(err_msg)
            raise ValueError(err_msg)

        # Check if file exists or if file can be created
        if not os.path.isfile(file_path):
            # logger.info("%s is not a file.", file_path)
            return False

        if not os.access(file_path, os.R_OK):
            # logger.info("%s is not readable.", file_path)
            return False

        if not os.access(file_path, os.W_OK):
            # logger.info("%s is not writable.", file_path)
            return False

        return True


    @staticmethod
    def dialog_select_file(
        dir_path: str = os.getcwd(),
        func: str = "open",
        opt : str = "All files (*.*)"
    ) -> str:
        """
        A static method that displays a dialog box for selecting a
        file.

        Parameters
        ----------
        dir_path : str
            The directory path to start the dialog box
            again. Defaults to the current working directory.
        func : str
            The function to perform with the selected file.
            Must be either "open" or "save". Defaults to "open".
        opt : str
            The file filter for the dialog box. Defaults to
            "All files (*.*)".

        Returns
        -------
        str
            The path of the selected file.

        Raises
        ------
        FileNotFoundError
            If the provided directory path is not
            invalid.
        ValueError
            If the provided function parameter is not
            "open" or "save".
        """
        # Initialize method variables
        qt_app  = QApplication([])
        if not GenericDir.test_dir(dir_path):
            err_msg = "No valid folder path was provided."
        #     logger.error(err_msg)
            raise FileNotFoundError(err_msg)

        # Control if func parameters are valid
        title = f"{func.capitalize()} a file"
        if func not in ["open", "save"]:
            err_msg  = f"Method cannot handle '{func}' func-parameter."
        #     logger.error(err_msg)
            raise ValueError(err_msg)

        # Show dialog box
        if func == "open":      # open dialog box
            path = QFileDialog.getOpenFileName(None, title, dir_path, opt)
            path = path[0]

        elif func == "save":    # save dialog box
            path = QFileDialog.getSaveFileName(None, title, dir_path, opt)
            path = f"{os.path.dirname(path[0])}{os.sep}{os.path.basename(path[0])}"

        else:
            err_msg  = f"Method cannot handle '{func}' func-parameter.)"
            # logger.error(err_msg)
            raise ValueError(err_msg)

        # Return path
        qt_app.closeAllWindows()
        # logger.info("File %s was selected.", path)
        return path




class GenericDir:
    """
    Represents a directory.

    Attributes
    ----------
    dir_path : str
        The path of the directory.
    file_class : object
        The class used to test if a file is valid.
    file_list : list[str]
        A list of file paths in the directory.
    """

    def __init__(
        self,
        dir_path: str = None,
        file_class: object = GenericFile
    ) -> None:
        """
        Initializes a new instance of the class.

        Parameters
        ----------
        dir_path : str
            The directory path to operate on.
            If not  provided, a dialog box is shown to select a
            directory. Defaults to None.
        file_class : object
            The class of files to be
            processed. Defaults to GenericFile.
        """
        # Select directory path if not provided
        if dir_path is None:
            dir_path  = GenericDir.dialog_select_dir()
        dir_path = os.path.abspath(dir_path)

        # Control if dir_path is valid
        if not GenericDir.test_dir(dir_path):
            err_msg = f"No valid directory path was provided ({dir_path})."
            # logger.error(err_msg)
            raise FileNotFoundError(err_msg)

        # Set instance attributes
        self.dir_path   = dir_path
        self.file_class = file_class

        # List all supported files in directory
        self.file_list = self.list_files(
            dir_path   = self.dir_path,
            recur      = True,
            file_class = self.file_class
        )


    def __str__(self) -> str:
        """
        Returns a string representation of the object.

        Parameters
        ----------
        self : object
            The object itself.

        Returns
        -------
        str
            The string representation of the object.
        """
        # Build the string
        class_name  = self.__class__.__name__
        return_str  = f"{class_name}(dir_path: {self.dir_path}"
        return_str += f" ; file_class: {self.file_class})"

        # Return the string
        return return_str


    def __eq__(self, __value: object) -> bool:
        """
        Check if the given value is equal to the current instance.

        Parameters
        ----------
        __value : object
            The value to compare with the current
            instance.

        Returns
        -------
        bool
            True if the value is equal to the current instance,
            False otherwise.
        """
        # Check if __value is a GenericDir instance
        if not isinstance(__value, GenericDir):
            return False

        # Test if __value is equal to self
        tmp_test = self.dir_path == __value.dir_path
        return tmp_test and (self.file_class == __value.file_class)


    @staticmethod
    def test_dir(dir_path: str):
        """
        Check if the given directory path is valid and accessible.

        Parameters
        ----------
        dir_path : str
            The directory path to be checked.

        Returns
        -------
        bool
            True if the directory path is valid and accessible,
            False otherwise.
        """
        # Check directory path and reformat it
        if dir_path is None:
            # logger.info("No directory path was provided.")
            return False

        # Check if directory exists or if directory can be created
        if not os.path.isdir(dir_path):
            # logger.info("%s does not exist.", dir_path)
            return False

        if os.path.isfile(dir_path):
            # logger.info("%s is a file, and not a folder.", dir_path)
            return False

        if not os.access(dir_path, os.R_OK):
            # logger.info("%s is not readable.", dir_path)
            return False

        if not os.access(dir_path, os.W_OK):
            # logger.info("%s is not writable.", dir_path)
            return False

        return True


    @staticmethod
    def dialog_select_dir(dir_path: str = os.getcwd()) -> str:
        """
        Selects a directory using a dialog box.

        Parameters
        ----------
        dir_path : str
            The initial directory path to be displayed
            in the dialog box. Defaults to the current working
            directory.

        Returns
        -------
        str
            The path of the selected directory.
        """
        # Initialize method variables
        qt_app  = QApplication([])
        if not GenericDir.test_dir(dir_path):
            err_msg = "No valid initial directory path was provided."
            # logger.error(err_msg)
            raise FileNotFoundError(err_msg)

        # Show dialog box and return path
        title = "Select a folder"
        path = QFileDialog.getExistingDirectory(None, title, dir_path)

        # Return path
        qt_app.closeAllWindows()
        # logger.info("Directory %s was selected.", path)
        return path


    @staticmethod
    def list_files(
        dir_path  : str,
        recur     : bool   = False,
        file_class: object =  GenericFile
    ) -> list[str]:
        """
        List all files in a directory.

        Parameters
        ----------
        dir_path : str
            The directory path.
        recur : bool
            Flag indicating whether to recursively search
            subdirectories. Defaults to False.
        file_class : object
            The class used to test if a file is valid.
            Defaults to GenericFile.

        Returns
        -------
        list[str]
            A list of file paths.
        """
        # Initialize method variables
        filelist = []

        # Build files list
        if file_class.test_file(dir_path):    # file path
            return dir_path

        if os.path.isdir(dir_path):     # folder path
            # Loop over all files within the folder
            for file in os.listdir(dir_path):
                file_path = dir_path + os.sep + file

                if file_class.test_file(file_path):     # file path
                    filelist.append(file_path)
                elif recur:                             # recursive search
                    filelist.extend(GenericDir.list_files(file_path, recur, file_class))

        return filelist
