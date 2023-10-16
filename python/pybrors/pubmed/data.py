"""
File: pubmed/data.py
"""

# Import packages and submodules
import copy
import pandas

# Import classes and methods
from pybrors.utils  import GenericDir
from pybrors.pubmed import PubmedFile


class PubmedData:
    """
    PUBMED data class.

    Attributes
    ----------
    file_dir : str
        The directory containing the file.
    file_list : list[str]
        A list of file names in the directory.
    articles : pandas.DataFrame
        All articles table.
    authors : pandas.DataFrame
        All authors table.
    keywords : pandas.DataFrame
        All keywords table.
    """

    WORDS_REMOVE = [
        "ci"
    ]
    """
    Class variable corresponding to all removed fields from wordcloud.
    """

    WORDS_REPLACE = {
        "à": "a", "â": "a", "é": "e", "è": "e", "ê": "e", "ô": "o", "ö": "o",
        "ù": "u", "û": "u",
        "computed tomography": "ct", "tomography, x-ray computed": "ct",
        "magnetic resonance imaging": "mri", "magnetic resonance": "mri",
        "mr ": "mri ", "mrs": "spectroscopy",
        "positron-emission tomography": "pet",
        "diagnostic imaging": "imaging",
        "adults": "adult", "agents": "agent",
        "children": "child", "complications": "complication",
        "drugs": "drug",
        "factors": "factor",
        "procedures": "procedure",
        "studies": "study",
        "tissues": "tissue", "trends": "trend",
        "ies ": "y ",
        "-": "_", "/": " ", "*": " ", ",": " ", "&": " ", "=": " ", ">": " ",
        "<": " ", ".": " "
    }
    """
    Class variable corresponding to all replaced words.
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
        # Initialize class attributes
        self.articles = ()
        self.authors = ()
        self.keywords = ()

        # Load a single PUBMED file
        if file_path is not None:
            self._get_file_data(file_path)

        # Load a PUBMED files from a directory
        elif dir_path is not None:
            self._get_dir_data(dir_path)

        else:
            err_msg = "No file or directory were provided to load PUBMED data."
            raise FileNotFoundError(err_msg)

    def _get_file_data(self, file_path: str) -> None:
        """
        Load PUBMED file from the given file path and extract its data.

        Parameters
        ----------
        file_path : str
            The path to the PUBMED file.
        """
        # Load PUBMED file
        tmp_file = PubmedFile(file_path=file_path)

        # Extract all data
        self.articles = tmp_file.articles
        self.authors  = tmp_file.authors
        self.keywords = tmp_file.keywords

    def _get_dir_data(self, dir_path: str) -> None:
        """
        Load PUBMED directory and extract all PUBMED info.

        Parameters
        ----------
        dir_path : str
            The path to the directory containing the PUBMED
            files.
        """
        # Get list of all files within the directory
        tmp_dir = GenericDir(dir_path=dir_path, file_class=PubmedFile)

        # Loop over all files
        if len(tmp_dir.file_list) > 0:
            # Load 1st PUBMED file and extract data
            print(tmp_dir.file_list[0])
            tmp_data = PubmedData(file_path=tmp_dir.file_list[0])

            if len(tmp_dir.file_list) > 1:
                for tmp_file_path in tmp_dir.file_list[1:]:
                    tmp_data += PubmedData(file_path=tmp_file_path)

            # Extract all data
            self.articles = tmp_data.articles
            self.authors  = tmp_data.authors
            self.keywords = tmp_data.keywords

    def __add__(self, other):
        """Left addition of PubMedFile."""
        result          = copy.deepcopy(self)

        #  Add new bibliography
        if isinstance(other, PubmedData):
            # Concatenate DataFrames
            result.articles = pandas.concat(
                    [result.articles, other.articles], ignore_index=True,
                    axis=0, join="outer")
            result.authors  = pandas.concat(
                    [result.authors, other.authors], ignore_index=True,
                    axis=0, join="outer")
            result.keywords = pandas.concat(
                    [result.keywords, other.keywords], ignore_index=True,
                    axis=0, join="outer")

            # Remove all duplicated lines
            result.articles.drop_duplicates(keep="first", inplace=True)
            result.authors.drop_duplicates(keep="first", inplace=True)
            result.keywords.drop_duplicates(keep="first", inplace=True)

        else:
            err_msg = f"Data type {type(other)} is not supported."
            raise TypeError(err_msg)

        return result

    def __radd__(self, other):
        """Right addition of PubMedFile."""
        return self.__add__(other)
