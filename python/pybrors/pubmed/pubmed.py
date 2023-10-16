"""
This file defines `PubMedFile` class to manipulate bibliography files
from PubMed search portal.

Author:
        benjamin.robert@philips.com
"""

# Import modules
import copy
import os
import pandas

# Import local methods
from .files                     import dialog_path, test_path
from wecstools.visualization    import display_wordcloud


class PubMedFile:
    """
    Class to import bibliography from PubMed.

    This class opens a file extracted from PubMed. It extracts and
    formats bibliography entries in `DataFrame`.

    Example
    -------
    >>> from wecstools.files import PubMedFile
    >>> from wecstools.files import list_dir
    >>> biblio_entry = PubMedFile(filepath=<FILE_PATH>)
    >>> biblio_entry.export_biblio()
    >>> biblio_entry.display_wordcloud(type="abstract")
    """

    TAGS_ARTICLE = ["PMID", "TI", "TA", "JT", "VI", "IP", "DP", "SO", "AB"]
    """
    Class variable corresponding to all extracted fields for articles db.
    """
    
    TAGS_AUTHOR  = ["PMID", "SAU", "FAU"]
    """
    Class variable corresponding to all extracted fields for authors db.
    """
    
    TAGS_KEYWORD = ["PMID", "MH"]
    """
    Class variable corresponding to all extracted fields for keywords db.
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
    
    def __init__(self, file_path: str = "") -> None:
        """
        The `PubMedFile` class constructor initializes class attributes
        and extracts publication information from a PubMed file.
                
        Args:
            file_path (str): Specify the path to a PubMed file. Default
                value is empty.
        """

        # Initialize class attributes
        self._path     = ""
        self._articles = pandas.DataFrame(columns=PubMedFile.TAGS_ARTICLE)
        self._authors  = pandas.DataFrame(columns=PubMedFile.TAGS_AUTHOR)
        self._keywords = pandas.DataFrame(columns=PubMedFile.TAGS_KEYWORD)

        # Initialize method variables
        author     = {}
        mesh       = {}
        pmid       = {}
        collect_ab = False

        # Validate file_path
        self._path = test_path(file_path) if file_path \
            else dialog_path(type="file", func="open")

        # Open PubMed file and extract publication info
        with open(self._path, "r") as file:
            for line in file:
                # Extract line info
                tag  = line[:4].strip()
                line = line[5:].strip()

                # Add new entry in _articles
                if tag == "PMID":
                    if pmid:    # add entry to articles dataframe
                        pmid = pandas.DataFrame(data=pmid, index=[0])
                        self._articles = pandas.concat(
                            [self._articles, pmid], ignore_index=True,
                            axis=0, join="outer"
                        )
                    pmid = {tag:line}   # initialize new entry

                elif tag in self._articles.columns:
                    pmid[tag] = self._clean_text(text=line)
                    collect_ab = True if tag == "AB" else False

                # Add new entry to _authors
                elif tag == "FAU":
                    # Reformat author line
                    short_name = self._clean_text(
                        text=line[:line.find(",")], keep_space=False
                    )

                    # Add new author entry
                    author = {"PMID":pmid["PMID"], "SAU":short_name, "FAU":line}
                    author = pandas.DataFrame(data=author, index=[0])
                    self._authors = pandas.concat(
                        [self._authors, author], ignore_index=True,
                        axis=0, join="outer"
                    )

                # Add new entry to keywords
                elif tag == "MH":
                    mesh = {"PMID":pmid["PMID"], "MH":self._clean_text(line)}
                    mesh = pandas.DataFrame(data=mesh, index=[0])
                    self._keywords = pandas.concat(
                        [self._keywords, mesh], ignore_index=True,
                        axis=0, join="outer"
                    )

                # Collect abstract
                elif collect_ab and not tag:
                    pmid["AB"] += self._clean_text(line)

                else:
                    collect_ab = False
            
        # Add last article and clean up data
        pmid = pandas.DataFrame(data=pmid, index=[0])
        self._articles = pandas.concat(
            [self._articles, pmid], ignore_index=True, axis=0, join="outer"
        )

        # Clean up all dataframes
        self._articles.fillna("", inplace=True)
        self._authors.fillna("", inplace=True)
        self._keywords.fillna("", inplace=True)
        self._articles["TA"] = self._articles["TA"].str.replace(" ", '_')

    def _clean_text(self, text: str, keep_space: bool = True) -> str:
        """
        The `_clean_text` function is formatting any string.

        This method replaces several groups of words by acronyms and
        can substitute spaces by `_`. The returned string is lower
        case.
        
        Args:
            text (str): Indicate the text to be cleaned.
            keep_space (bool): Keep the spaces in the text or not.
                Default value is True
        
        Returns:
            The text in lower cases, substitutes groups of words by
            acronyms and replaces spaces by underscores
        """
        
        # Control text input
        if not isinstance(text, str) or text is None:
            err_msg = "text input value should be a string and cannot be empty."
            raise ValueError(err_msg)

        # Switch to lower cases and clean up text
        text = text.lower().strip()
        for old,new in self.WORDS_REPLACE.items():
            text = text.replace(old, new)

        # Replace space by _
        if keep_space:  return text.strip()
        else:           return text.replace(" ", "_").strip()

    def __add__(self, other):
        """Left addition of PubMedFile."""
        result = copy.deepcopy(self)

        #  Add new bibliography
        if isinstance(other, PubMedFile):
            # Concatenate DataFrames
            result._articles = pandas.concat(
                    [result._articles, other._articles], ignore_index=True,
                    axis=0, join="outer")
            result._authors  = pandas.concat(
                    [result._authors, other._authors], ignore_index=True,
                    axis=0, join="outer")
            result._keywords = pandas.concat(
                    [result._keywords, other._keywords], ignore_index=True,
                    axis=0, join="outer")

            # Remove all duplicated lines
            result._articles.drop_duplicates(keep="first", inplace=True)
            result._authors.drop_duplicates(keep="first", inplace=True)
            result._keywords.drop_duplicates(keep="first", inplace=True)

            return result

        else:
            err_msg = f"Data type {type(other)} is not supported."
            raise TypeError(err_msg)

    def __radd__(self, other):
        """Right addition of PubMedFile."""
        return self.__add__(other)

    def export_biblio(self, file_path: str = "") -> None:
        """
        Export bibliography to Excel file. This method is used to
        export bibliography data to Excel file.

        Args:
            file_path (str): Path to export to. If not specified a
                dialog will be shown to the user.
        """

        try:

            # Control file to be exported
            file_path = test_path(file_path) if file_path \
                else dialog_path(
                    dir_path=os.path.dirname(self._path), type="file",
                    func="save", opt="Excel file (*.xlsx)"
                )

            # Save bibliography databases
            writer = pandas.ExcelWriter(file_path, engine="xlsxwriter")
            self._articles.to_excel(writer, sheet_name="articles", index=False)
            self._authors.to_excel(writer, sheet_name="authors", index=False)
            self._keywords.to_excel(writer, sheet_name="keywords",index=False)
            writer.close()

        except FileNotFoundError:
            raise FileNotFoundError(f"{file_path} was not found.")

        print(f"DB was saved to {file_path}")

    def display_wordcloud(
        self, type: str = "keyword", remove_words: str = []
    ) -> None:
        """
        The `display_wordcloud` function generates a wordcloud out of
        biblio db.
        
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
        remove_words += list(PubMedFile.WORDS_REMOVE)
        data = {
            "keyword" : self._keywords.MH ,
            "author"  : self._authors.SAU,
            "journal" : self._articles.TA ,
            "title"   : self._articles.TI ,
            "abstract": self._articles.AB
        }

        # Extract data to be displayed
        if type in data.keys():
            tmp_txt = " ".join(i for i in data[type] if len(i) > 1)
        else:
            raise ValueError(f"Type {type} is not recognized.")

        # Create word cloud
        display_wordcloud(
            text=tmp_txt, remove_words=remove_words, fig_width=1000)
