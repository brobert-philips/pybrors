"""
File: tests/test_pubmed.py
"""

# Import packages and submodules

# Import classes and methods
from pybrors.pubmed import PubmedData


def test_pubmed():
    """
    Test the PubmedData class.

    This function demonstrates the usage of the PubmedData class by
    creating instances from different data sources and performing
    various operations.
    """
    # Local variables
    xlsx_file = "ext/data/pubmed/pubmed_bibliography.xlsx"

    # Create PubmedData instance from a pubmed text file
    tmp = PubmedData(file_path="ext/data/pubmed/references_millet.pubmed")
    tmp.export_bibliography(file_path=xlsx_file)

    # Create PubmedData instance from a pubmed directory
    tmp = PubmedData(dir_path="ext/data/pubmed")
    tmp.export_bibliography(file_path=xlsx_file)

    # Create PubmedData instance from a pubmed text file
    tmp = PubmedData(bib_path=xlsx_file)

    # Display title
    print("Title")
    tmp.display_wordcloud(data_type="title")
