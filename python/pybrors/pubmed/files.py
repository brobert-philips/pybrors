# File: pubmed/files.py

# Import packages and submodules
import os
import pandas

# Import classes and methods
from pybrors.utils  import GenericFile

class PubmedFile(GenericFile):

    """
    PUBMED file class inheriting from GenericFile.

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

    TAGS_ARTICLE = ["PMID", "TI", "TA", "JT", "VI", "IP", "DP", "SO", "AB"]
    """
    Class variable corresponding to all extracted fields for articles db.
    """

    TAGS_AUTHOR  = ["PMID", "SAU", "FAU", "AD"]
    """
    Class variable corresponding to all extracted fields for authors db.
    """

    TAGS_KEYWORD = ["PMID", "MH"]
    """
    Class variable corresponding to all extracted fields for keywords db.
    """

    FILE_TYPES = {
        ""       : "All files"  ,
        ".pubmed": "PUBMED files",
    }
    """Supported file extensions."""

    def __init__(self, file_path: str = None) -> None:
        """
        Initializes a PUBMED file object.

        Parameters
        ----------
        file_path : str
            The absolute path of the PUBMED file. If not provided, a
            file selection dialog will be displayed.

        Raises
        ------
        FileNotFoundError
            If the file path is invalid or the file is not supported.
        """
        # Initialize parent attributes
        super().__init__(file_path)

        # Initialize class attributes
        self.articles = pandas.DataFrame(columns=self.TAGS_ARTICLE)
        self.authors  = pandas.DataFrame(columns=self.TAGS_AUTHOR)
        self.keywords = pandas.DataFrame(columns=self.TAGS_KEYWORD)

        # Initialize method variables
        author     = {}
        mesh       = {}
        pmid       = {}
        collect_ab = False
        collect_ad = False

        # Open PubMed file and extract publication info
        with open(self.file_path, "r", encoding = "utf8") as file:
            for line in file:
                # Extract line info
                tag  = line[:4].strip()
                line = line[5:].strip()

                # Add new entry in articles
                if tag == "PMID":
                    if pmid:    # add entry to articles dataframe
                        pmid = pandas.DataFrame(data=pmid, index=[0])
                        self.articles = pandas.concat(
                            [self.articles, pmid], ignore_index=True,
                            axis=0, join="outer"
                        )
                    pmid = {tag:line}   # initialize new entry

                # Add new entry in authors
                elif tag == "FAU":
                    if author:    # add entry to authors dataframe
                        author["SAU"] = self._clean_text(
                            text=author["FAU"][:author["FAU"].find(",")],
                            keep_space=False
                        )
                        author["PMID"] = pmid["PMID"]
                        author = pandas.DataFrame(data=author, index=[0])
                        self.authors = pandas.concat(
                            [self.authors, author], ignore_index=True,
                            axis=0, join="outer"
                        )
                    author = {tag:line}   # initialize new entry

                # Add new entry to keywords
                elif tag == "MH":
                    mesh = {"PMID":pmid["PMID"], "MH":self._clean_text(line)}
                    mesh = pandas.DataFrame(data=mesh, index=[0])
                    self.keywords = pandas.concat(
                        [self.keywords, mesh], ignore_index=True,
                        axis=0, join="outer"
                    )

                # Extract tags according to specific conditions
                elif tag in self.articles.columns:
                    pmid[tag] = self._clean_text(text=line)
                    collect_ab = tag == "AB"

                elif tag in self.authors.columns:
                    author[tag] = self._clean_text(text=line)
                    collect_ad = tag == "AD"

                elif collect_ab and not tag:
                    pmid["AB"] += self._clean_text(line)

                elif collect_ad and not tag:
                    author["AD"] += self._clean_text(line)

                else:
                    collect_ab = False
                    collect_ad = False

        # Add last article and clean up data
        pmid = pandas.DataFrame(data=pmid, index=[0])
        self.articles = pandas.concat(
            [self.articles, pmid], ignore_index=True, axis=0, join="outer"
        )

        # Add last author and clean up data
        author["SAU"] = self._clean_text(
            text=author["FAU"][:author["FAU"].find(",")], keep_space=False
        )
        author["PMID"] = pmid["PMID"]
        author = pandas.DataFrame(data=author, index=[0])
        self.authors = pandas.concat(
            [self.authors, author], ignore_index=True, axis=0, join="outer"
        )

    @staticmethod
    def test_file(file_path: str = None) -> bool:
        """
        Test if file exists, is readable and is a PUBMED supported file.

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

        # Test if file extension is "pubmed"
        extension = os.path.splitext(file_path)[1]
        if extension != ".pubmed":
            return False

        # Read the first 4 characters of the file
        with open(file_path, "rt", encoding="utf8") as file:
            first_4_chars = file.read(4)

        # Check if the first 4 characters are "PMID"
        if first_4_chars != "PMID":
            return False

        return True

    def _clean_text(self, text: str, keep_space: bool = True) -> str:
        """
        The `_clean_text` function is formatting any string.

        This method replaces several groups of words by acronyms and
        can substitute spaces by `_`. The returned string is lower
        case.

        Parameters
        ----------
        text : str
            Indicate the text to be cleaned.
        keep_space : bool
            Keep the spaces in the text or not. Default value is True.

        Returns
        -------
        str
            The text in lower cases, substitutes groups of words by
            acronyms and replaces spaces by underscores
        """

        # Control text input
        if not isinstance(text, str) or text is None:
            err_msg = "text input value should be a string and cannot be empty."
            raise ValueError(err_msg)

        # Switch to lower cases and clean up text
        text = text.lower().strip()

        # Replace space by _
        if keep_space:
            return text.strip()
        else:
            return text.replace(" ", "_").strip()
