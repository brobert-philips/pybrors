"""
File: pubmed/data.py
"""

# Import packages and submodules
import copy
import pandas

# Import classes and methods
from pybrors.utils  import GenericDir, display_wordcloud, GenericFile
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

        # Clean up all dataframes
        self.articles.fillna("", inplace=True)
        self.authors.fillna("", inplace=True)
        self.keywords.fillna("", inplace=True)
        self.articles["TA"] = self.articles["TA"].str.replace(" ", '_')

    def display_wordcloud(
        self, data_type: str = "keyword", remove_words: str = None
    ) -> None:
        """
        The `display_wordcloud` function generates a wordcloud out of
        bibliography database.

        The wordcloud graph is built out of one of the bibliography
        category. Several words are removed natively and additional
        words can be removed.

        Args:
            type (str): Select the data to be used for wordcloud.
                Values can be `keyword`, `author`, `journal`, `title`,
                `abstract`.
            stopwords (str): Remove words that are not relevant to the
                visualization
        """
        # Initialize method variables
        if remove_words is None:
            remove_words = []
        remove_words += list(self.WORDS_REMOVE)
        data = {
            "keyword" : self.keywords.MH ,
            "author"  : self.authors.SAU,
            "journal" : self.articles.TA ,
            "title"   : self.articles.TI ,
            "abstract": self.articles.AB
        }

        # Extract data to be displayed
        if data_type in data:
            tmp_txt = " ".join(i for i in data[data_type] if len(i) > 1)
        else:
            raise ValueError(f"Type {data_type} is not recognized.")

        # Replace words
        for old,new in self.WORDS_REPLACE.items():
            tmp_txt = tmp_txt.replace(old, new)

        # Create word cloud
        display_wordcloud(
            text=tmp_txt, remove_words=remove_words, fig_width=1540, fig_height=1000)

    def export_bibliography(self, file_path: str = None) -> None:
        """
        Export bibliography to Excel file.

        Args:
            file_path (str): Path to export to. If not specified a
                dialog will be shown to the user.
        """
        # Test if file exists and is writable
        if file_path is None:
            file_path = GenericFile.dialog_select_file(
                dir_path=self.dir_path,
                func="save",
                opt="Excel file (*.xlsx)"
            )
        else:
            if not GenericFile.test_file(file_path):
                raise FileNotFoundError(f"{file_path} was not found.")

        # Save bibliography databases
        writer = pandas.ExcelWriter(file_path, engine="xlsxwriter")
        self.articles.to_excel(writer, sheet_name="articles", index=False)
        self.authors.to_excel(writer, sheet_name="authors", index=False)
        self.keywords.to_excel(writer, sheet_name="keywords",index=False)
        writer.close()
        print(f"DB was saved to {file_path}")

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

        # Extract directory information
        self.dir_path = tmp_file.file_dir

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
            tmp_data = PubmedData(file_path=tmp_dir.file_list[0])

            if len(tmp_dir.file_list) > 1:
                for tmp_file_path in tmp_dir.file_list[1:]:
                    tmp_data += PubmedData(file_path=tmp_file_path)

            # Extract all data
            self.articles = tmp_data.articles
            self.authors  = tmp_data.authors
            self.keywords = tmp_data.keywords

        # Extract directory information
        self.dir_path = tmp_dir.dir_path

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
