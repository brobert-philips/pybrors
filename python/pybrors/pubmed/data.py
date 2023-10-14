"""
File: pubmed/data.py
"""

# Import packages and submodules

# Import classes and methods
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

    def __init__(self, file_path: str = None) -> None:
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

        # Extract file information
        self.file_dir   = tmp_file.file_dir
        self.file_list = [tmp_file.file_name]
