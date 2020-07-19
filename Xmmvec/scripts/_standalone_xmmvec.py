# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import click

from Xmmvec.xmmvec import xmmvec
from Xmmvec import __version__


@click.command()
@click.option(
    "-r", "--i-ranks-path", required=True,
    help="Path to mmvec ranks."
)
@click.option(
    "-o", "--o-ranks-explored", required=False,
    help="Path to the output explorer visualization."
)
@click.option(
    "-t", "--i-tree-taxonomy", required=False, default="",
    help="Path to a tree which internal nodes are labeled."
)
@click.option(
    "-m1", "--p-omic1-metadata", required=False, default="",
    help="{Path to the metadata table for omic1 features "
                            "(columns of the ranks matrix)."
)
@click.option(
    "-c1", "--p-omic1-column", required=False, default="",
    help="Column from metadata to use for "
         "stratification of omic1 features."
)
@click.option(
    "-f1", "--p-omic1-filt", required=False, default="",
    help="Column from metadata `-m1` to use for "
         " filtering based on values of `-f1`."
)
@click.option(
    "-v1", "--p-omic1-value", required=False, default="", multiple=True,
    help="Filter omic1 features based on"
         " column passed to `-f1`."
)
@click.option(
    "-n1", "--p-omic1-name", required=False, default="omic1",
    show_default=True, help="Name for omic1 features."
)
@click.option(
    "-m2", "--p-omic2-metadata", required=False, default="",
    help="{Path to the metadata table for omic2 features "
         "(rows of the ranks matrix)."
)
@click.option(
    "-c2", "--p-omic2-column", required=False, default="",
    help="Column from metadata to use for "
         "stratification of omic2 features."
)
@click.option(
    "-f2", "--p-omic2-filt", required=False, default="",
    help="Column from metadata `-m2` to use for "
         " filtering based on values of `-f2`."
)
@click.option(
    "-v2", "--p-omic2-value", required=False, default="", multiple=True,
    help="Filter omic2 features based on"
         " column passed to `-f2`."
)
@click.option(
    "-n2", "--p-omic2-name", required=False, default="omic2",
    show_default=True, help="Name for omic2 features."
)
@click.option(
    "-p", "--p-min-probability", default=0., show_default=True, type=float,
    help="Minimum conditional probability."
)
@click.option(
    "-n", "--p-pair-number", default=10, show_default=True, type=int,
    help="initial number of co-occurrences per feature."
)
@click.option(
    "-x1", "--p-omic1-max", default=50, show_default=True, type=int,
    help="Maximum number of co-occurrences per omic1 feature."
)
@click.option(
    "-x2", "--p-omic2-max", default=50, show_default=True, type=int,
    help="Maximum number of co-occurrences per omic2 feature."
)
@click.option(
    "-col", "--p-color-palette", default='rainbow', show_default=True,
    type=click.Choice(['blues', 'greens', 'oranges', 'reds', 'purples', 'greys', 'viridis',
                       'magma', 'inferno', 'plasma', 'bluegreen', 'bluepurple', 'greenblue',
                       'orangered', 'purplebluegreen', 'purpleblue', 'purplered', 'redpurple',
                       'yellowgreenblue', 'yellowgreen', 'yelloworangebrown', 'yelloworangered',
                       'blueorange', 'brownbluegreen', 'purplegreen', 'pinkyellowgreen',
                       'purpleorange', 'redblue', 'redgrey', 'redyellowblue', 'redyellowgreen',
                       'spectral', 'rainbow', 'sinebow']),
    help="Color palette for the heatmap."
)
@click.option(
    "--verbose/--no-verbose", default=False
)
@click.version_option(__version__, prog_name="Xmmvec")


def standalone_xmmvec(
        i_ranks_path,
        o_ranks_explored,
        i_tree_taxonomy,
        p_omic1_metadata,
        p_omic1_column,
        p_omic1_filt,
        p_omic1_value,
        p_omic1_name,
        p_omic2_metadata,
        p_omic2_column,
        p_omic2_filt,
        p_omic2_value,
        p_omic2_name,
        p_min_probability,
        p_pair_number,
        p_color_palette,
        p_omic1_max,
        p_omic2_max,
        verbose
):

    xmmvec(
        i_ranks_path,
        o_ranks_explored,
        i_tree_taxonomy,
        p_omic1_metadata,
        p_omic1_column,
        p_omic1_filt,
        p_omic1_value,
        p_omic1_name,
        p_omic2_metadata,
        p_omic2_column,
        p_omic2_filt,
        p_omic2_value,
        p_omic2_name,
        p_min_probability,
        p_pair_number,
        p_color_palette,
        p_omic1_max,
        p_omic2_max,
        verbose
    )


if __name__ == "__main__":
    standalone_xmmvec()
