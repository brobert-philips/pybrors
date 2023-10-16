"""
This file defines Python methods which are displaying data/images.

Author:
        benjamin.robert@philips.com
"""

# Import modules
import numpy
import pandas
import re
import matplotlib.colors    as colors
import plotly.express       as px
import plotly.graph_objects as go

# Import classes
from matplotlib import pyplot
from wordcloud  import WordCloud

# Import variables
from wordcloud import STOPWORDS


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


def plot_data1d(
    data: pandas.DataFrame, type: str = "line",
    xlabel: str = "", ylabel: str = "", clabel: str = ""
) -> None:
    """
    Plot 1D data.

    This is a function to plot 1D data.

    Args:
        data (pandas.DataFrame): Data to plot in one dimension. The
            columns must be unique (`x`, `y`, `cat`).
        type (str): Plot type (`line`, `stack`, `percent`). Default is
            `line`.
        xlabel (str): Label for x-axis.
        ylabel (str): Label for y-axis.
        clabel (str): Label for color-axis.
    """
    
    # Initialize variables
    if "color" not in data.columns:         data["color"] = ""
    if "line_group" not in data.columns:    data["line_group"] = ""

    # Build plot
    if type == "line":
        fig = px.line(
            data, x="x", y="y",
            color="color", color_discrete_sequence=COLORS,
            labels={"x": xlabel, "y": ylabel, "color": clabel}
        )
        
    elif type in ["stack", "percent"]:
        groupnorm = "percent" if type == "percent" else ""
        fig = px.area(
            data, x="x", y="y", line_group="line_group",
            color= "color", color_discrete_sequence=COLORS,
            labels={"x": xlabel, "y": ylabel, "color": clabel},
            groupnorm=groupnorm
        )

    else:
        raise ValueError(f"Plot type {type} is not supported.")

    # Specific changes according to data type    
    if type == "percent":
        fig.update_layout(yaxis_range=(0, 100))
        fig.update_layout(yaxis_title="Percentage (%)")
        
    # Update plot area style
    fig.update_layout(template="simple_white")
    fig.update_xaxes(mirror=True, showgrid=True, gridcolor="#D8D4D7")
    fig.update_yaxes(mirror=True, showgrid=True, gridcolor="#D8D4D7")
    
    fig.show()
