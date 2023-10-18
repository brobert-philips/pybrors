# File: utils/plotdata.py

# Import packages and submodules
import re
import numpy
import matplotlib.colors    as colors

# Import classes and methods
from matplotlib import pyplot
from wordcloud  import STOPWORDS, WordCloud


# COLORS = colors.ListedColormap([
COLORS = [
        "#0077CD", "#DE7C00", "#269A91", "#D10077", "#008540", "#8345BA",
        "#658E1E", "#F04279", "#00A9EB", "#FFA40D", "#5CB9BB", "#EB6FBD",
        "#009C49", "#A77AD7", "#65A812", "#FC9BC1"
]
"""Constant containing the Philips colors palette."""


def display_wordcloud(
    text: str = "",
    remove_words: str = [],
    fig_width: int = 500,
    fig_height: int = 500
) -> None:
    """
    The `display_wordcloud` function takes a string of text and plots
    the wordcloud.

    It also accepts an optional list of words to be removed from the wordcloud.

    Args:
        text (str): Pass a string of words to the function
        remove_words (str): Remove words from the wordcloud
        fig_width (int): Width of the wordcloud figure
        fig_height (int): Height of the wordcloud figure
    """

    # Format data to be displayed
    text = re.sub(r"[^a-zA-Z0-9 _]", "", text).split(" ")
    text = " ".join(word for word in text if len(word) > 1)
    remove_words += STOPWORDS

    # Build wordcloud object
    x, y = numpy.ogrid[:fig_height, :fig_width]
    wc_mask = ((x/fig_height - 1/2) ** 2 + (y/fig_width - 1/2) ** 2) > 0.49 ** 2
    wc_mask = 255 * wc_mask.astype(int)
    wc_object = WordCloud(
        width=fig_width, height=fig_height,
        background_color="white", colormap=colors.ListedColormap(COLORS),
        mask=wc_mask,
        max_words = 200, max_font_size = 100, stopwords=remove_words,
    ).generate(text)

    # Show figure
    pyplot.imshow(wc_object, interpolation="spline36")
    pyplot.axis("off")
    pyplot.show()

    print(wc_object.words_)
